"""Real pilot, user-study and laboratory analyses. No automatic synthetic substitutions."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from .io import require_columns,require_unique


def pilot_quality(records,reviews):
    require_columns(records,["record_id","collection_group_id","domain"])
    require_columns(reviews,["record_id","reviewer_id","attribute","value","minutes"])
    if not set(reviews.record_id).issubset(set(records.record_id)):raise ValueError("Unknown pilot reference ID")
    counts=reviews.groupby(["record_id","attribute"]).reviewer_id.nunique()
    disagreements=reviews.groupby(["record_id","attribute"]).value.nunique()
    return {"records":len(records),"groups":records.collection_group_id.nunique(),"minimum_reviewers_per_attribute":int(counts.min()),
       "disagreement_fraction":float((disagreements>1).mean()),"total_review_minutes":float(pd.to_numeric(reviews.minutes).sum()),
       "median_review_minutes":float(pd.to_numeric(reviews.minutes).median()),"domain_counts":records.domain.value_counts().to_dict(),
       "note":"Descriptive feasibility audit. This does not approve the schema or power the final study."}


def user_study_analysis(df,B=1000,seed=0):
    require_columns(df,["participant_id","arm","comprehension_correct","appropriate_reliance","elapsed_seconds"])
    if (df.groupby("participant_id").arm.nunique()>1).any():raise ValueError("This analysis is for the registered parallel-arm design, not an undeclared crossover")
    for c in ["comprehension_correct","appropriate_reliance"]:
        if not pd.to_numeric(df[c]).between(0,1).all():raise ValueError("Outcome outside [0,1]")
    means=df.groupby(["participant_id","arm"])[["comprehension_correct","appropriate_reliance","elapsed_seconds"]].mean().reset_index()
    arms=sorted(means.arm.unique())
    if len(arms)!=2:raise ValueError("Exactly two prespecified arms required")
    rng=np.random.default_rng(seed);results={}
    for metric in ["comprehension_correct","appropriate_reliance","elapsed_seconds"]:
        a=means.loc[means.arm==arms[1],metric].to_numpy(float);b=means.loc[means.arm==arms[0],metric].to_numpy(float)
        if min(len(a),len(b))<3:raise ValueError("Too few independent participants")
        samples=rng.choice(a,(B,len(a)),replace=True).mean(1)-rng.choice(b,(B,len(b)),replace=True).mean(1)
        results[metric]={"contrast":f"{arms[1]}-{arms[0]}","difference":float(a.mean()-b.mean()),"ci95":np.quantile(samples,[.025,.975]).tolist(),"participants_per_arm":[len(b),len(a)]}
    return results


def assay_qc(df):
    require_columns(df,["specimen_id","analyte","batch_id","concentration","lod","loq","censored","units","qc_pass"])
    require_unique(df,["specimen_id","analyte"])
    if df.units.nunique()!=1:raise ValueError("Harmonise assay units explicitly before analysis")
    numeric=df[["concentration","lod","loq"]].apply(pd.to_numeric,errors="coerce")
    if (numeric.lod<0).any() or (numeric.loq<numeric.lod).any():raise ValueError("Invalid detection/quantification limits")
    cens=df.censored.astype(str).str.lower().isin(["true","1"])
    if numeric.concentration[~cens].isna().any():raise ValueError("Uncensored record missing concentration")
    return {"specimens":df.specimen_id.nunique(),"analytes":df.analyte.unique().tolist(),"batches":df.batch_id.nunique(),
            "censored_rows":int(cens.sum()),"qc_failed":int((~df.qc_pass.astype(str).str.lower().isin(["true","1"])).sum()),
            "policy":"Censored records retained. No LOD/2 substitution or concentration inference is performed by this QC function."}


def assay_detected_sensitivity(df,image_features,preparation_features):
    """Optional detected-only EXPLORATORY comparison, explicitly not the primary censored analysis."""
    assay_qc(df)
    if df.analyte.nunique()!=1:raise ValueError("Analyse one specified analyte at a time")
    keep=~df.censored.astype(str).str.lower().isin(["true","1"])
    keep&=df.qc_pass.astype(str).str.lower().isin(["true","1"])
    y=pd.to_numeric(df.loc[keep,"concentration"]).to_numpy(float);groups=df.loc[keep,"batch_id"].to_numpy()
    if len(np.unique(groups))<3:raise ValueError("At least 3 independent preparation/assay groups required")
    xs={"image_only":np.asarray(image_features)[keep],"preparation_only":np.asarray(preparation_features)[keep]}
    xs["combined"]=np.column_stack(list(xs.values()));rows=[]
    for name,x in xs.items():
        pred=np.full(len(y),np.nan)
        for tr,te in GroupKFold(min(5,len(np.unique(groups)))).split(x,y,groups):
            model=make_pipeline(StandardScaler(),Ridge(alpha=1.));model.fit(x[tr],y[tr]);pred[te]=model.predict(x[te])
        rows.append({"model":name,"mae":float(np.mean(np.abs(y-pred))),"n_detected":len(y),"scope":"detected_only_exploratory_not_censoring_corrected"})
    return pd.DataFrame(rows)
