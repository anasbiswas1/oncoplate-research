"""Explicit overlapping-task adapters. No inferred cancer or preparation ground truth."""
from pathlib import Path
import time,csv,json
import pandas as pd
import requests
from .io import write_json,read_json,utcnow,require_columns


def lookup_product(barcode,cache_dir,user_agent,refresh=False,api_version="v3.6"):
    """One user-selected OFF product; retained snapshot, no bulk scraping or invented labels."""
    code=str(barcode)
    if not code.isdigit() or not 8<=len(code)<=14:raise ValueError("Expected an 8–14 digit barcode")
    if not user_agent or "@" not in user_agent:raise ValueError("Supply project User-Agent with contact email")
    dest=Path(cache_dir)/f"{code}.json"
    if dest.exists() and not refresh:return read_json(dest)
    if api_version not in ("v3.6","v2"):raise ValueError("Unreviewed API version")
    url=f"https://world.openfoodfacts.org/api/{api_version}/product/{code}.json"
    rate_file=Path(cache_dir)/"last_request.json"
    if rate_file.exists():
        wait=4.2-(time.time()-float(read_json(rate_file)["unix_time"]))
        if wait>0:time.sleep(wait)
    write_json(rate_file,{"unix_time":time.time()})
    fields="code,product_name,brands,ingredients_text,ingredients,labels_tags,categories_tags,last_modified_t,image_front_url,image_ingredients_url"
    response=requests.get(url,params={"fields":fields},headers={"User-Agent":user_agent},timeout=40)
    response.raise_for_status();data=response.json()
    result={"barcode":code,"retrieved_at":utcnow(),"source_url":url,"record":data,
            "package_match_confirmed":False,"requires_human_product_verification":True,
            "licence_note":"Database/content/images have separate OFF terms. Public lookup is not a confirmed formulation or chemical assay."}
    write_json(dest,result);return result


def nutrition5k_metadata(path):
    """Parse official dish_metadata.csv variable-length ingredient blocks.
    dish_id + five dish totals, then repeated (ingredient_id,name,mass,kcal,fat,carb,protein).
    Raises on mismatched schema rather than interpreting arbitrary columns.
    """
    dishes=[];ingredients=[]
    with open(path,newline="") as f:
        for row in csv.reader(f):
            if not row:continue
            if row[0]=="dish_id":continue
            if len(row)<6:raise ValueError("Incomplete Nutrition5k dish row")
            # The README lists num_ingrs and seven named repeated fields, but says eight.
            # Accept ONLY a validated seven-field block, with optional matching count.
            if (len(row)-6)%7==0 and (len(row)==6 or row[6].startswith("ingr_")):
                offset=6
            elif (len(row)-7)%7==0 and row[6].isdigit() and int(row[6])==(len(row)-7)//7:
                offset=7
            else:raise ValueError("Unexpected Nutrition5k schema; inspect the source rather than guessing")
            rid=row[0]
            dishes.append(dict(zip(["record_id","total_calories","total_mass_g","total_fat_g","total_carb_g","total_protein_g"],row[:6])))
            for j in range(offset,len(row),7):
                vals=row[j:j+7]
                if not vals[0].startswith("ingr_"):raise ValueError("Malformed ingredient block")
                ingredients.append(dict(record_id=rid,**dict(zip(["ingredient_id","ingredient_name","mass_g","calories","fat_g","carb_g","protein_g"],vals))))
    return pd.DataFrame(dishes),pd.DataFrame(ingredients)


def map_external_ingredients(ingredients,reviewed_crosswalk):
    require_columns(reviewed_crosswalk,["ingredient_id","target_value","review_reference"])
    if not reviewed_crosswalk.review_reference.astype(str).str.len().gt(0).all():raise ValueError("Unreviewed ingredient crosswalk")
    if reviewed_crosswalk.ingredient_id.duplicated().any():raise ValueError("Ambiguous ingredient crosswalk")
    out=ingredients.merge(reviewed_crosswalk,on="ingredient_id",how="left",validate="many_to_one")
    out["mapped"]=out.target_value.notna()
    return out


def prepare_external_cohort(cfg,cohort_id,import_root,review_reference):
    """Create an immutable cohort addendum without touching the main split/schema/targets."""
    from datetime import datetime
    from .config import paths
    from .governance import verify_lock,require_gate,make_lock
    from .datasets import ingest_documented
    from .splits import build_components
    from .targets import load_targets,make_targets,save_targets
    from .inputs import validate_states
    from .io import read_table,write_table,sha256
    if not cohort_id.replace('_','').replace('-','').isalnum():raise ValueError("Use a simple cohort identifier")
    if not review_reference:raise ValueError("External duplicate/group review reference required")
    require_gate(cfg,'new_collection');p=paths(cfg);lock=verify_lock(p['private']/'analysis_lock.json')
    root=p['private']/'external'/cohort_id;root.mkdir(parents=True,exist_ok=True)
    if (root/'cohort_lock.json').exists():
        verify_lock(root/'cohort_lock.json');return root
    import_root=Path(import_root)
    external,ann=ingest_documented(import_root/'records.jsonl',import_root/'annotations.jsonl',root/'prepared',allowed_root=import_root)
    if not external.cohort.eq('external').all():raise ValueError("Only the predeclared external cohort is permitted here")
    if 'captured_at' not in external:raise ValueError("Fresh prospective records need capture timestamps")
    cutoff=datetime.fromisoformat(lock['created_at'])
    if any(datetime.fromisoformat(str(v).replace('Z','+00:00'))<=cutoff for v in external.captured_at):
        raise ValueError("This fresh-prospective route requires post-lock capture. Earlier external data need a separately registered retrospective protocol.")
    main=read_table(p['prepared']/'study_records.csv')
    if set(main.record_id)&set(external.record_id):raise ValueError("Repeated record IDs across main/external")
    combined=build_components(pd.concat([main,external],ignore_index=True))
    eg=set(combined[combined.record_id.isin(external.record_id)].group_id);mg=set(combined[combined.record_id.isin(main.record_id)].group_id)
    if eg&mg:raise ValueError("External records share a known acquisition group, duplicate or product family with main data")
    external=combined[combined.record_id.isin(external.record_id)].copy();external['split']='external'
    write_table(root/'prepared/study_records.csv',external)
    if 'focal_item_id' in external:
        ann=ann.merge(external[['record_id','focal_item_id']],on='record_id',validate='many_to_one')
        ann=ann[ann.focal_item_id.eq('__record__')|ann.item_id.eq(ann.focal_item_id)]
    for head in ['independent','joint']:
        schema=load_targets(p['prepared']/f'targets_{head}')['schema']
        save_targets(make_targets(external,ann,schema),root/'prepared'/f'targets_{head}')
    states=read_json(import_root/'inference_states.json');validate_states(external,states)
    write_json(root/'inference_states.json',states)
    files=[root/'prepared/study_records.csv',root/'inference_states.json',root/'prepared/targets_joint/targets.npz',root/'prepared/targets_independent/targets.npz']
    make_lock(root/'cohort_lock.json',files,{'cohort_id':cohort_id,'parent_analysis_lock':lock['lock_hash'],'group_review_reference':review_reference,'claim':'fresh_prospective_no_retuning'})
    return root


def external_frozen_predictions(cfg,cohort_id):
    from .config import paths
    from .governance import verify_lock,record_unblinding
    from .training import predict_run
    from .targets import load_targets
    from .io import read_table,write_table,write_jsonl,atomic_npz
    from .calibration import probabilities
    from .benchmark import candidate_rows,make_rating_jobs
    from .evaluation import score_candidates,policy_predictions
    p=paths(cfg);lock=verify_lock(p['private']/'analysis_lock.json');protocol=lock['protocol']
    root=p['private']/'external'/cohort_id;verify_lock(root/'cohort_lock.json')
    record_unblinding(p['private']/'analysis_lock.json',root/'first_access.json',cohort_id)
    records=read_table(root/'prepared/study_records.csv');states=read_json(root/'inference_states.json');rules=read_json(p['private']/'claim_rules.json')
    allpred=[]
    for run_id in protocol['run_ids']:
        run=p['runs']/run_id;spec=read_json(run/'run.json')['spec'];targets=load_targets(root/'prepared'/f"targets_{spec['head']}")
        pred=predict_run(run,records,targets,p['features']/f'external_{cohort_id}')
        atomic_npz(root/f'{run_id}_visual_predictions.npz',**pred);pred['probabilities']=probabilities(pred['logits'])
        cc,objects=candidate_rows(records,pred,targets['schema'],states,rules,asof=read_json(root/'cohort_lock.json')['created_at'],input_mode=protocol['input_mode'])
        write_table(root/f'{run_id}_candidates.csv',cc);write_jsonl(root/f'{run_id}_objects.jsonl',objects);make_rating_jobs(cc,root/f'{run_id}_rating_jobs.csv')
        sel=p['private']/'selectors'/run_id;scored=score_candidates(cc,sel,read_json(sel/'chosen_support_calibrators.json'))
        pp=policy_predictions(scored,read_json(sel/'operating_thresholds.json'),target=protocol['target_coverage'],seed=spec['seed'])
        write_table(root/f'{run_id}_frozen_policy_predictions.csv',pp);allpred.append(pp)
    out=pd.concat(allpred,ignore_index=True);write_table(root/'predictions_before_ratings.csv',out)
    return out
