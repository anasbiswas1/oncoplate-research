"""Locked, information-matched selective evaluation with independent reference ratings."""
from pathlib import Path
import numpy as np
import pandas as pd
from .io import read_json,write_json,write_table,read_table,digest
from .selection import load_selector,choose_threshold
from .statistics import bool_series,analysis_weights,assertion_metrics
from .calibration import fit_temperature,fit_sigmoid,probabilities
from .benchmark import adjudicated_ratings,join_ratings


def score_candidates(candidates,selector_dir,calibrators=None):
    """No labels or reference fields are used by this function."""
    out=candidates.copy();calibrators=calibrators or {}
    for name in ("generic","pcsi"):
        model,features=load_selector(Path(selector_dir)/f"{name}.json")
        logits=model.logits(out[features].to_numpy(float))
        out[f"{name}_score"]=probabilities(logits,calibrators.get(name)).ravel()
    conf=np.clip(out.candidate_confidence.to_numpy(float),1e-7,1-1e-7)
    z=np.log(conf)-np.log1p(-conf)
    out["joint_confidence_score"]=probabilities(z,calibrators.get("joint_confidence")).ravel()
    return out


def fit_support_calibrators(candidates,ratings,selector_dir,out):
    if not candidates.split.eq("calibration").all():raise ValueError("Support calibration uses only calibration rows")
    joined=join_ratings(candidates,ratings)
    observed=joined.support_status.isin(["supported","contradicted","unverifiable"])
    data=joined[observed]
    if data.empty:raise ValueError("No independently rated informative calibration claims")
    y=data.support_status.eq("supported").to_numpy(float)
    result={}
    for name in ("generic","pcsi"):
        model,features=load_selector(Path(selector_dir)/f"{name}.json")
        z=model.logits(data[features].to_numpy(float))
        result[name]={"identity":{"kind":"identity"},"temperature":fit_temperature(z,y),"sigmoid":fit_sigmoid(z,y)}
    conf=np.clip(data.candidate_confidence.to_numpy(float),1e-7,1-1e-7)
    z=np.log(conf)-np.log1p(-conf)
    result["joint_confidence"]={"identity":{"kind":"identity"},"temperature":fit_temperature(z,y),"sigmoid":fit_sigmoid(z,y)}
    write_json(out,result);return result


def selected_calibrators(all_calibrators,kind="temperature"):
    return {k:v[kind] for k,v in all_calibrators.items()}


def policy_thresholds(scored_validation,out,*,mixture=None,targets=(.5,.7,.8,.9)):
    if not scored_validation.split.eq("validation").all():raise ValueError("Only validation can choose deployment thresholds")
    w=analysis_weights(scored_validation,mixture)
    informative=bool_series(scored_validation.informative).to_numpy()
    gate=bool_series(scored_validation.eligible).to_numpy()
    methods={"M2":("joint_confidence_score",informative),"M3":("generic_score",informative),
             "M6":("joint_confidence_score",informative&gate),"M7":("pcsi_score",informative&gate)}
    result={m:{str(t):choose_threshold(scored_validation[col].to_numpy(float),eligible,t,w) for t in targets}
            for m,(col,eligible) in methods.items()}
    write_json(out,result);return result


def policy_predictions(scored,thresholds,*,target=.8,seed=0):
    """Freeze predictions BEFORE merging reference outcomes. Same one focal candidate per record."""
    informative=bool_series(scored.informative).to_numpy();gate=bool_series(scored.eligible).to_numpy()
    frames=[]
    for m,col,eligible in [("M2","joint_confidence_score",informative),("M3","generic_score",informative),
                           ("M6","joint_confidence_score",informative&gate),("M7","pcsi_score",informative&gate)]:
        df=scored.copy();df["method"]=m;df["seed"]=int(seed);df["score"]=df[col].to_numpy(float)
        df["accepted"]=eligible & (df.score.to_numpy()>=thresholds[m][str(target)]["threshold"])
        df["question_count"]=0;df["target_coverage"]=target;frames.append(df)
    return pd.concat(frames,ignore_index=True)


def attach_outcomes(predictions,ratings):
    ratings=ratings[["candidate_id","support_status"]].drop_duplicates()
    if ratings.candidate_id.duplicated().any():raise ValueError("Conflicting candidate adjudication")
    out=predictions.merge(ratings,on="candidate_id",how="left",validate="many_to_one")
    if out.support_status.isna().any():raise ValueError("Missing ratings. Do not fill missing reference with supported")
    # A rubric that judges a candidate non-informative always overrides model-side specificity.
    out["informative"]=bool_series(out.informative)&out.support_status.ne("noninformative")
    return out


def evaluate_results(df,mixture=None):
    rows=[]
    for (method,seed),part in df.groupby(["method","seed"]):
        rows.append({"method":method,"seed":int(seed),**assertion_metrics(part,mixture)})
    return pd.DataFrame(rows)


def oof_claim_candidates(cfg,spec,state_inputs,rules,*,asof,input_mode="multimodal",device=None):
    """Create actual focal claims using fold-local models; no in-sample confidence."""
    from .pipeline import load_study
    from .config import paths
    from .selection import oof_predictors,validate_oof_ledger
    from .benchmark import candidate_rows
    from .io import write_jsonl
    records,targets=load_study(cfg,spec.head,stage_images=True);p=paths(cfg)
    root=p["runs"]/"oof"/spec.run_id
    ledger=oof_predictors(records,targets,spec,root,p["features"]/"oof"/spec.run_id,cfg["study"]["oof_folds"],device)
    dfs=[];objs=[]
    for fold,part in ledger.groupby("fold"):
        with np.load(root/f"fold_{fold}"/"heldout_predictions.npz",allow_pickle=False) as z:pred={k:z[k] for k in z.files}
        pred["probabilities"]=probabilities(pred["logits"])
        rr=records.set_index("record_id").loc[pred["ids"]].reset_index()
        cc,oo=candidate_rows(rr,pred,targets["schema"],state_inputs,rules,asof=asof,input_mode=input_mode)
        cc=cc.merge(part[["record_id","fold","training_group_ids","early_stop_group_ids"]],on="record_id",validate="one_to_one")
        dfs.append(cc);objs.extend(oo)
    out=pd.concat(dfs,ignore_index=True);validate_oof_ledger(out)
    write_table(root/"oof_claim_candidates.csv",out);write_jsonl(root/"oof_claim_objects.jsonl",objs)
    return out
