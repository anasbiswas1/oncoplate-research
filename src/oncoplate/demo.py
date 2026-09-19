"""Synthetic software tests ONLY. The images are not meals; no scientific claim may use them."""
from pathlib import Path
import copy,json
import numpy as np
import pandas as pd
from PIL import Image
from .config import initialize,paths
from .io import write_json,write_jsonl,write_table,read_json,sha256
from .datasets import image_hashes
from .pipeline import prepare_study,load_study,run_training,spec_from_cfg,calibrate_predictor,partition_predictions
from .selection import oof_predictors,SoftLogistic,GENERIC_FEATURES,PROVENANCE_FEATURES,train_selectors
from .benchmark import candidate_rows,make_rating_jobs,adjudicated_ratings
from .evaluation import fit_support_calibrators,score_candidates,selected_calibrators,policy_thresholds,policy_predictions,attach_outcomes,evaluate_results
from .statistics import paired_bootstrap
from .governance import make_lock
from .calibration import probabilities


def create_fixture(cfg,groups=32):
    if cfg.get("mode")!="demo":raise PermissionError("Synthetic fixtures must use DEMO_ONLY configuration")
    p=initialize(cfg);rows=[];ann=[];states={};truth={};rng=np.random.default_rng(723)
    for g in range(groups):
        for j,domain in enumerate(["meal","product"]):
            rid=f"DEMO_g{g:03d}_{j}";item="item0";value=["red","green"][g%2]
            arr=rng.integers(0,30,(32,32,3),dtype=np.uint8);arr[:,:,g%2]+=150
            image=p["raw"]/f"{rid}.png";Image.fromarray(arr).save(image)
            h,dh,w,hh=image_hashes(image)
            rows.append({"record_id":rid,"image_path":str(image),"domain":domain,"collection_group_id":f"G{g:03d}",
                         "sha256":h,"dhash":dh,"width":w,"height":hh,"synthetic":True,"source":"software_fixture"})
            truth[rid]=value
            for reviewer in ["a","b"]:
                observed=value if reviewer=="a" or g%7 else ["red","green"][1-g%2]
                ann.append({"record_id":rid,"item_id":item,"reviewer_id":reviewer,"category":"synthetic_object", "subcategory":observed,
                  "cooking_style":["vertical","horizontal"][g%2],"review_complete":True,"reference_kind":"synthetic_only"})
            sources=[]
            if g%3:
                # Known fixture facts; occasional conflicts exercise the gate, not a biological process.
                sources=[{"source_id":rid+"_s","record_id":rid,"item_id":item,"source_type":"recipe_record",
                         "facts":{"subcategory":value},"observed_at":"2026-09-01T00:00:00+00:00","available_at_inference":True,
                         "reference_only":False,"verification_status":"reviewed","conflict":g%11==0}]
            states[rid]={"focal_field":"subcategory","focal_item_id":item,"visual_scope":"single_item","sources":sources}
    write_table(p["prepared"]/"records.csv",pd.DataFrame(rows));write_table(p["prepared"]/"annotations.csv",pd.DataFrame(ann))
    write_json(p["private"]/"inference_states.json",states);write_json(p["private"]/"fixture_truth.json",truth)
    write_json(p["prepared"]/"dataset_audit.json",{"synthetic_only":True,"records":len(rows),"groups":groups,"not_food":True})
    return pd.DataFrame(rows),pd.DataFrame(ann)


def fixture_rules():
    return {"subcategory":{"claim_id":"fixture_visual","fields":["subcategory"],"values":["red","green"],
           "qualifiers":["predicted","recorded"],"documentary_for_recorded":True,"specificity":1}}


def fixture_ratings(candidates,truth):
    # Used exclusively for synthetic SOFTWARE assertions. Real research requires independent adjudication.
    rows=[]
    for r in candidates.itertuples():
        factual="supported" if r.value==truth[r.record_id] else "contradicted"
        evidential="supported" if bool(r.eligible) else "unknown"
        rows.append({"candidate_id":r.candidate_id,"factual_status":factual,"evidential_status":evidential,
                     "informative":bool(r.informative),"adjudication_id":"SYNTHETIC_TEST_ONLY"})
    return adjudicated_ratings(pd.DataFrame(rows))


def run_demo(cfg,*,bootstrap=100,include_oof=True):
    import torch
    torch.set_num_threads(2)
    if cfg.get("mode")!="demo":raise PermissionError("The demo cannot write to research paths")
    create_fixture(cfg);records,_=prepare_study(cfg);p=paths(cfg)
    cfg["training"].update(head_epochs=4,max_epochs=2,head_batch_size=16,batch_size=8,effective_batch_size=16,image_size=32,patience=3)
    result={"synthetic_only":True,"biological_experiments":0}
    for head in ["independent","joint"]:
        spec=spec_from_cfg(cfg,"tiny_demo","frozen",head,0);run_training(cfg,spec,device="cpu")
    spec=spec_from_cfg(cfg,"tiny_demo","frozen","joint",0);run=p["runs"]/spec.run_id
    calibrate_predictor(cfg,spec.run_id,device="cpu")
    rr,targets=load_study(cfg,"joint");rules=fixture_rules();states=read_json(p["private"]/"inference_states.json");truth=read_json(p["private"]/"fixture_truth.json")
    selector_dir=p["private"]/"selectors";selector_dir.mkdir(exist_ok=True)
    if include_oof:
        from .evaluation import oof_claim_candidates
        oof=oof_claim_candidates(cfg,spec,states,rules,asof="2026-09-18T00:00:00+00:00",device="cpu")
    else:
        raise ValueError("Full demo deliberately exercises OOF; do not skip it for a validation claim")
    ratings=fixture_ratings(oof,truth);train_selectors(oof,ratings,selector_dir)
    candidates={};rated={}
    for partition in ("calibration","validation"):
        pred=partition_predictions(cfg,spec.run_id,partition,device="cpu");pred["probabilities"]=probabilities(pred["logits"])
        sub=rr.set_index("record_id").loc[pred["ids"]].reset_index()
        cc,_=candidate_rows(sub,pred,targets["schema"],states,rules)
        candidates[partition]=cc;rated[partition]=fixture_ratings(cc,truth)
    calpath=selector_dir/"calibrators.json"
    cals=fit_support_calibrators(candidates["calibration"],rated["calibration"],selector_dir,calpath)
    chosen=selected_calibrators(cals)
    scored=score_candidates(candidates["validation"],selector_dir,chosen)
    thresholds=policy_thresholds(scored,selector_dir/"thresholds.json",mixture=cfg["study"]["domain_mixture"])
    lock=p["private"]/"analysis_lock.json"
    if not lock.exists():make_lock(lock,[run/"best.pt",selector_dir/"generic.json",selector_dir/"pcsi.json",calpath,selector_dir/"thresholds.json"],{"synthetic_only":True,"primary":"M7-M3"})
    pred=partition_predictions(cfg,spec.run_id,"test",device="cpu",allow_unblind=True);pred["probabilities"]=probabilities(pred["logits"])
    sub=rr.set_index("record_id").loc[pred["ids"]].reset_index();cc,_=candidate_rows(sub,pred,targets["schema"],states,rules)
    scored=score_candidates(cc,selector_dir,chosen);pp=policy_predictions(scored,thresholds)
    out=attach_outcomes(pp,fixture_ratings(cc,truth));write_table(p["reports"]/"SYNTHETIC_results.csv",out)
    table=evaluate_results(out,cfg["study"]["domain_mixture"]);write_table(p["reports"]/"SYNTHETIC_metrics.csv",table)
    stats,replicates=paired_bootstrap(out,mixture=cfg["study"]["domain_mixture"],B=bootstrap)
    write_json(p["reports"]/"SYNTHETIC_paired_intervals.json",stats)
    from .export import export_run
    exported=export_run(run,p["exports"]/"fixture")
    result.update(status="completed",stages=["fixture","targets","splits","two_heads","OOF","selectors","calibration","lock","test","paired_statistics","export"],
                  test_records=len(sub),oof_records=len(oof),export=exported)
    write_json(p["reports"]/"software_demo_validation.json",result);return result
