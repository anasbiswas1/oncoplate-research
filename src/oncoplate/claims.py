"""Finite provenance-constrained claims. No exposure tiers or invented chemical truth."""
from __future__ import annotations
from dataclasses import dataclass,field,asdict
from datetime import datetime,timezone
from itertools import product
from typing import Any
from .io import digest

UNKNOWN="__unknown__"
DOC_TYPES={"ingredient_panel","manufacturer_record","recipe_record","preparation_log","reviewed_product_record"}


@dataclass
class Source:
    source_id:str
    record_id:str
    item_id:str
    source_type:str
    facts:dict
    observed_at:str
    available_at_inference:bool=True
    reference_only:bool=False
    verification_status:str="unreviewed"
    content_hash:str=""
    conflict:bool=False

    def __post_init__(self):
        for key in ("available_at_inference","reference_only","conflict"):
            if type(getattr(self,key)) is not bool:raise ValueError(f"Source {key} must be a JSON boolean")
        if not isinstance(self.facts,dict):raise ValueError("Source facts must be a mapping")


@dataclass
class Claim:
    candidate_id:str
    record_id:str
    item_id:str
    claim_id:str
    field:str
    value:str
    qualifier:str
    confidence:float
    informative:bool=True
    specificity:int=1
    evidence_id:str=""


@dataclass
class State:
    record_id:str
    item_id:str
    alternatives:list[dict]
    sources:list[Source]=field(default_factory=list)
    predicted:dict=field(default_factory=dict)
    unknown_mass:float=1.0
    reference_only:bool=False


def visible_sources(state):
    if state.reference_only:raise ValueError("Reference-only state cannot be used at inference")
    out=[]
    for s in state.sources:
        if s.record_id!=state.record_id or s.item_id!=state.item_id:
            raise ValueError("Cross-record/item source binding")
        if s.available_at_inference and not s.reference_only:out.append(s)
    return out


def make_state(record_id,item_id,predicted,sources,*,required_fields=None):
    required_fields=required_fields or list(predicted)
    stub=State(record_id,item_id,[],sources,predicted)
    visible=visible_sources(stub)
    alternatives={};unknown_count=0
    for field in required_fields:
        values={str(s.facts[field]) for s in visible if field in s.facts and s.verification_status=="reviewed" and not s.conflict}
        if not values:
            raw=predicted.get(field,{})
            values=set(raw.get("alternatives",[]))|{str(raw.get("value",UNKNOWN)),UNKNOWN}
            unknown_count+=1
        alternatives[field]=sorted(values)
    # Bound finite enumeration and NEVER silently discard the unknown alternative.
    n=1
    for vals in alternatives.values():n*=len(vals)
    if n>4096:raise ValueError("Completion set exceeds 4096; narrow the registered focal claim, not the hidden uncertainty")
    states=[dict(zip(alternatives,vs)) for vs in product(*alternatives.values())]
    return State(record_id,item_id,states,visible,predicted,unknown_count/max(len(required_fields),1))


def eligibility(claim:Claim,state:State,rule:dict):
    if (claim.record_id,claim.item_id)!=(state.record_id,state.item_id):raise ValueError("Claim/item mismatch")
    sources=visible_sources(state)
    if claim.value not in rule.get("values",[]):return False,"value_outside_registered_vocabulary"
    if claim.qualifier not in rule.get("qualifiers",[]):return False,"qualifier_not_permitted"
    if claim.field not in rule.get("fields",[]):return False,"field_not_permitted"
    if not state.alternatives:return False,"empty_completion_set"
    relevant=[s for s in sources if claim.field in s.facts]
    facts={str(s.facts[claim.field]) for s in relevant if s.verification_status=="reviewed"}
    if any(s.conflict for s in relevant) or len(facts)>1:return False,"critical_source_conflict"
    if claim.qualifier=="predicted":
        pred=state.predicted.get(claim.field,{})
        if str(pred.get("value",UNKNOWN))!=claim.value:return False,"missing_visual_prediction"
        if not 0<=claim.confidence<=1:return False,"invalid_confidence"
        return True,"qualified_prediction_only"
    if claim.qualifier in ("recorded","observed"):
        required=rule.get("documentary_for_recorded",True)
        qualified=[s for s in relevant if s.verification_status=="reviewed" and (s.source_type in DOC_TYPES or (claim.qualifier=="observed" and s.source_type=="reviewed_visual_annotation"))]
        if required and not any(str(s.facts.get(claim.field))==claim.value for s in qualified):return False,"missing_reviewed_premise"
        if any(str(z.get(claim.field,UNKNOWN))!=claim.value for z in state.alternatives):return False,"not_supported_across_completions"
        return True,"supported_by_available_premises"
    return False,"non_focal_claim"


def source_features(claim,state,*,asof):
    sources=visible_sources(state);now=datetime.fromisoformat(asof.replace("Z","+00:00"))
    ages=[]
    for s in sources:
        when=datetime.fromisoformat(s.observed_at.replace("Z","+00:00"))
        ages.append(max(0.,(now-when).total_seconds()/86400))
    relevant=[s for s in sources if claim.field in s.facts]
    return {"n_sources":float(len(sources)),"has_documentary":float(any(s.source_type in DOC_TYPES for s in relevant)),
            "source_age_days":min(max(ages,default=0.),3650.),"missing_premises":float(not relevant),
            "source_conflicts":float(any(s.conflict for s in relevant) or len({str(s.facts[claim.field]) for s in relevant})>1),
            "unknown_mass":float(state.unknown_mass)}


def support_status(factual_status,evidential_status,informative=True):
    if not informative:return "noninformative"
    if factual_status=="contradicted":return "contradicted"
    if factual_status=="supported" and evidential_status=="supported":return "supported"
    if factual_status in ("supported","unknown","unverifiable") and evidential_status in ("supported","unknown","unverifiable","unsupported"):
        return "unverifiable"
    raise ValueError("Invalid independently assigned reference axes")


def render(claim,state,rule,*,score,threshold,reviewed_rule=False):
    ok,reason=eligibility(claim,state,rule)
    if not reviewed_rule:
        return {"status":"research_preview_only","reason":"claim_schema_pending_domain_review","informative":False}
    if not ok or score<threshold:
        return {"status":"not_established","reason":reason if not ok else "support_score_below_threshold",
                "message":"The available information does not establish this attribute. This is not a safety verdict.","informative":False}
    value=str(claim.value)
    # Values are finite enum values in the registered schema, not arbitrary package-text instructions.
    if value not in rule.get("values",[]):raise ValueError("Value outside approved wording vocabulary")
    templates={"predicted":"The model predicts {field}: {value}.","recorded":"The available record states {field}: {value}.","observed":"The reviewed image records {field}: {value}."}
    return {"status":"answer","claim":asdict(claim),"message":templates[claim.qualifier].format(field=claim.field.replace("_"," "),value=value),
            "support_score":float(score),"informative":bool(claim.informative),"source_ids":[s.source_id for s in visible_sources(state)],"reason":reason}


def state_from_dict(data):
    if set(data)-{"record_id","item_id","alternatives","sources","predicted","unknown_mass","reference_only"}:raise ValueError("Unknown or hidden fields in inference state")
    d=dict(data);d["sources"]=[Source(**s) for s in d.get("sources",[])]
    return State(**d)


def claim_from_dict(data):return Claim(**data)
