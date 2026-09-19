"""Finite action replay. A recorded answer is not a simulated real user trial."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from .selection import GENERIC_FEATURES,PROVENANCE_FEATURES

ACTIONS=("barcode_lookup","ingredient_panel","component_identity","preparation_detail")


def replay_answer(answers,record_id,action):
    if action not in ACTIONS:raise ValueError("Action outside registered menu")
    matches=[a for a in answers if a["record_id"]==record_id and a["action_id"]==action]
    if len(matches)>1:raise ValueError("Ambiguous response episode; key by episode explicitly")
    if not matches or not matches[0].get("available",False):return {"available":False,"value":"unknown","idealised_replay":True}
    a=matches[0]
    if not a.get("source_id"):raise ValueError("Available response lacks documentary provenance")
    return {**a,"idealised_replay":True}


class GainPolicy:
    """Fit development action episodes; no access to the future answer at action selection."""
    def __init__(self,seed=0,penalty=1.,cost_weight=.05):
        self.seed=seed;self.penalty=penalty;self.cost_weight=cost_weight;self.models={}
        self.features=GENERIC_FEATURES+PROVENANCE_FEATURES
    def fit(self,episodes):
        if not episodes.split.eq("fit").all():raise ValueError("Action policy training accepts fitting episodes only")
        missing=set(self.features+["supported_gain","unsupported_gain","cost_units","action_id"])-set(episodes)
        if missing:raise ValueError(f"Missing development action fields {missing}")
        for a,df in episodes.groupby("action_id"):
            if a not in ACTIONS:raise ValueError("Unexpected action")
            target=df.supported_gain-self.penalty*df.unsupported_gain-self.cost_weight*df.cost_units
            model=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=7,min_samples_leaf=5,l2_regularization=1.,random_state=self.seed)
            model.fit(df[self.features].to_numpy(float),target.to_numpy(float));self.models[a]=model
        if set(self.models)!=set(ACTIONS):raise ValueError("Missing action coverage; do not fabricate counterfactual action rewards")
        return self
    def choose(self,state_features,available_menu=ACTIONS):
        scores={a:float(self.models[a].predict(np.array([[state_features[k] for k in self.features]],float))[0]) for a in available_menu}
        best=max(scores,key=scores.get)
        return (best if scores[best]>0 else "no_action"),scores


def baseline_action(policy,features,seed=0,menu=ACTIONS):
    if policy=="fixed":return "ingredient_panel" if "ingredient_panel" in menu else menu[0]
    if policy=="random":return str(np.random.default_rng(seed).choice(menu))
    if policy=="uncertainty":
        # Registered heuristic, not posterior access to the hidden answer.
        return "ingredient_panel" if features.get("missing_premises",0)>0 else "preparation_detail"
    raise ValueError("Unknown baseline")


def action_replay(records,answers,policy,feature_fn,update_fn,evaluate_fn,*,budget=1,seed=0):
    if budget not in (0,1,2):raise ValueError("Budget must be predeclared")
    rows=[]
    for i,r in enumerate(records):
        state=r;before=evaluate_fn(state);actions=[];elapsed=0.
        for t in range(budget):
            feat=feature_fn(state)
            action=policy.choose(feat)[0] if hasattr(policy,"choose") else baseline_action(policy,feat,seed+i*31+t)
            if action=="no_action" or action in actions:break
            answer=replay_answer(answers,r["record_id"],action)
            actions.append(action);elapsed+=float(answer.get("elapsed_seconds",0))
            state=update_fn(state,action,answer)
        after=evaluate_fn(state)
        rows.append({"record_id":r["record_id"],"n_actions":len(actions),"actions":actions,"elapsed_seconds":elapsed,"before":before,"after":after,"idealised_replay":True})
    return rows


def replay_focal_candidates(candidates,objects,answers,policy,rules,*,asof,budget=1,seed=0):
    """Outputs predictions/rating jobs only. Outcome gain is scored AFTER independent review.
    Counterfactual answers are used only from documented real records and flagged idealised.
    """
    from dataclasses import asdict
    from .claims import claim_from_dict,state_from_dict,Source,make_state,eligibility,source_features,DOC_TYPES
    from .io import digest
    from .benchmark import make_rating_jobs
    if budget not in (0,1):raise ValueError("This controlled implementation is zero/one action; two-step learning is a separate extension")
    by={o['claim']['candidate_id']:o for o in objects};rows=[];out_objects=[]
    for i,row in enumerate(candidates.to_dict('records')):
        obj=by[row['candidate_id']];claim=claim_from_dict(obj['claim']);state=state_from_dict(obj['state'])
        action='no_action';answer={'available':False};cost=0
        if budget:
            action=policy.choose(row)[0] if hasattr(policy,'choose') else baseline_action(policy,row,seed+i)
            if action!='no_action':answer=replay_answer(answers,claim.record_id,action);cost=1
        srcs=list(state.sources)
        if answer.get('available'):
            if 'source' not in answer:raise ValueError("Documented replay answer needs an explicit Source object")
            src=Source(**answer['source'])
            if (src.record_id,src.item_id)!=(claim.record_id,claim.item_id):raise ValueError("Clarification answered the wrong item")
            srcs.append(src)
        newstate=make_state(claim.record_id,claim.item_id,state.predicted,srcs,required_fields=[claim.field])
        vals={str(s.facts[claim.field]) for s in newstate.sources if claim.field in s.facts and s.source_type in DOC_TYPES and s.verification_status=='reviewed' and not s.conflict}
        if len(vals)==1:claim.value=next(iter(vals));claim.qualifier='recorded'
        claim.candidate_id=digest({'before':row['candidate_id'],'claim':asdict(claim),'sources':[asdict(s) for s in newstate.sources]})[:24]
        ok,why=eligibility(claim,newstate,rules[claim.field]);rr=dict(row)
        rr.update(candidate_id=claim.candidate_id,before_candidate_id=row['candidate_id'],value=claim.value,qualifier=claim.qualifier,
                  eligible=ok,gate_reason=why,action_id=action,question_count=cost,elapsed_seconds=float(answer.get('elapsed_seconds',0)),
                  idealised_replay=True,**source_features(claim,newstate,asof=asof))
        rows.append(rr);out_objects.append({'claim':asdict(claim),'state':asdict(newstate)})
    return pd.DataFrame(rows),out_objects
