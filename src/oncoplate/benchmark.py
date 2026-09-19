"""Candidate generation from visible inputs; reference joins occur only in rating/evaluation."""
from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
import numpy as np
import pandas as pd
from .claims import Claim,Source,make_state,eligibility,source_features,UNKNOWN,support_status
from .io import digest,write_table,write_jsonl,read_jsonl,require_unique


def candidate_rows(records,predictions,schema,state_inputs,rules,*,asof="2026-09-18T00:00:00+00:00",input_mode="multimodal"):
    """The focal field and item are specified BEFORE reading outcome/reference fields.
    Multimodal late fusion uses only reviewed, currently visible documentary premises.
    All compared selectors receive exactly these same candidates.
    """
    if input_mode not in ("image_only","metadata_only","multimodal"):raise ValueError("Unknown input mode")
    labels=[json.loads(l) for l in schema["labels"]]
    prediction_index={r:i for i,r in enumerate(predictions["ids"])}
    rows=[];objects=[]
    for r in records.to_dict("records"):
        rid=r["record_id"]
        if rid not in state_inputs:raise ValueError(f"Missing inference-state record for {rid}")
        s=state_inputs[rid]
        if any(k in s for k in ("support_status","ground_truth","reference_labels","y_support")):raise ValueError("Reference fields in visible state")
        field=s["focal_field"];item=s["focal_item_id"];rule=rules[field]
        probs=np.asarray(predictions["probabilities"])[prediction_index[rid]]
        js=[j for j,l in enumerate(labels) if field in l]
        predicted={};confidence=0.
        visual_scope=s.get("visual_scope","record_presence")
        binding_available=(visual_scope in ("single_item","focal_crop") or item=="__record__")
        # A whole-meal classifier cannot silently assign its top tuple to an arbitrary item.
        if js and input_mode!="metadata_only" and binding_available:
            j=max(js,key=lambda k:probs[k]);value=str(labels[j][field]);confidence=float(probs[j])
            alternatives=sorted({str(labels[k][field]) for k in js if probs[k]>=.1})
            predicted[field]={"value":value,"alternatives":alternatives,"confidence":confidence}
        else:value=UNKNOWN
        sources=[] if input_mode=="image_only" else [Source(**x) for x in s.get("sources",[])]
        state=make_state(rid,item,predicted,sources,required_fields=[field])
        qualified="predicted"
        docs=[x for x in state.sources if field in x.facts and x.verification_status=="reviewed" and not x.conflict]
        documented={str(x.facts[field]) for x in docs}
        if input_mode!="image_only" and len(documented)==1:
            value=next(iter(documented));qualified="recorded"
            # Documentary agreement is a feature, not a declared calibrated probability of truth.
        if value not in rule.get("values",[]):value=UNKNOWN
        if value==UNKNOWN:qualified="recorded"
        cid=digest({"record_id":rid,"item_id":item,"field":field,"value":value,"qualifier":qualified,
                    "input_mode":input_mode,"visible_sources":[asdict(x) for x in state.sources]})[:24]
        claim=Claim(cid,rid,item,rule["claim_id"],field,value,qualified,confidence,informative=value!=UNKNOWN,specificity=rule.get("specificity",1))
        ok,reason=eligibility(claim,state,rule)
        entropy=float(-(np.clip(probs,1e-8,1-1e-8)*np.log(np.clip(probs,1e-8,1-1e-8))+(1-np.clip(probs,1e-8,1-1e-8))*np.log1p(-np.clip(probs,1e-8,1-1e-8))).mean())
        row={"record_id":rid,"group_id":r["group_id"],"domain":r["domain"],"split":r["split"],"candidate_id":cid,
             "field":field,"value":value,"qualifier":qualified,"input_mode":input_mode,"candidate_confidence":confidence,
             "joint_marginal_gap":float(s.get("predicted_joint_marginal_gap",0.)),"entropy":entropy,"specificity":claim.specificity,
             "informative":claim.informative,"eligible":ok,"gate_reason":reason,**source_features(claim,state,asof=asof)}
        rows.append(row);objects.append({"claim":asdict(claim),"state":asdict(state)})
    return pd.DataFrame(rows),objects


def make_rating_jobs(candidates,output,seed=0):
    require_unique(candidates,["candidate_id"])
    keep=["candidate_id","record_id","field","value","qualifier","input_mode"]
    jobs=candidates[keep].sample(frac=1,random_state=seed).copy()
    jobs["blinded_job_id"]=[f"J{i:06d}" for i in range(len(jobs))]
    for col in ("reviewer_id","factual_status","evidential_status","informative","reason_code","adjudication_id"):jobs[col]=""
    # No model identity, confidence, gate decision, or predicted support in blinded jobs.
    write_table(output,jobs);return jobs


def adjudicated_ratings(ratings):
    require_unique(ratings,["candidate_id"])
    if not ratings.adjudication_id.astype(str).str.len().gt(0).all():raise ValueError("Missing adjudication reference")
    df=ratings.copy()
    informative=df.informative.astype(str).str.lower().isin(["true","1"])
    df["support_status"]=[support_status(f,e,i) for f,e,i in zip(df.factual_status,df.evidential_status,informative)]
    return df


def join_ratings(candidates,ratings):
    require_unique(candidates,["candidate_id"]);require_unique(ratings,["candidate_id"])
    out=candidates.merge(ratings[["candidate_id","support_status"]],on="candidate_id",how="left",validate="one_to_one")
    if out.support_status.isna().any():raise ValueError("Unrated candidate output; never assume unsupported=0")
    return out
