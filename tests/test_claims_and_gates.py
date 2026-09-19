import dataclasses
import numpy as np
import pandas as pd
import pytest
from oncoplate.claims import *
from oncoplate.governance import *
from oncoplate.inputs import validate_states
from oncoplate.benchmark import candidate_rows,adjudicated_ratings
from oncoplate.io import write_json

RULE={'fields':['processing_status'],'values':['processed','unprocessed'], 'qualifiers':['predicted','recorded'],'documentary_for_recorded':True}

def source(value='processed',**kwargs):
    x=dict(source_id='s',record_id='r',item_id='i',source_type='ingredient_panel',facts={'processing_status':value},observed_at='2026-09-01T00:00:00+00:00',verification_status='reviewed');x.update(kwargs);return Source(**x)

def claim(qualifier='recorded',value='processed'):
    return Claim('c','r','i','processing','processing_status',value,qualifier,.9)

def state(sources=None):return make_state('r','i',{'processing_status':{'value':'processed','alternatives':['processed','unprocessed']}},sources or [])

def test_missing_processing_not_confirmed():assert not eligibility(claim(),state(),RULE)[0]
def test_qualified_visual_prediction_allowed():assert eligibility(claim('predicted'),state(),RULE)[0]
def test_reviewed_fact_allowed():assert eligibility(claim(),state([source()]),RULE)[0]
def test_unreviewed_not_confirmed():assert not eligibility(claim(),state([source(verification_status='unreviewed')]),RULE)[0]
def test_conflict_abstains():assert not eligibility(claim(),state([source(),source('unprocessed',source_id='t')]),RULE)[0]
def test_unknown_retained():assert any(z['processing_status']==UNKNOWN for z in state().alternatives)
def test_empty_set_not_vacuous():
    s=state();s.alternatives=[];assert not eligibility(claim(),s,RULE)[0]
def test_hidden_reference_not_used():assert not eligibility(claim(),state([source(reference_only=True)]),RULE)[0]
def test_cross_item_rejected():
    with pytest.raises(ValueError):state([source(item_id='other')])
def test_reference_state_rejected():
    s=state();s.reference_only=True
    with pytest.raises(ValueError):visible_sources(s)
def test_information_deletion_does_not_enable_recorded():
    assert eligibility(claim(),state([source()]),RULE)[0]
    assert not eligibility(claim(),state(),RULE)[0]
def test_renderer_needs_domain_review():assert render(claim(),state([source()]),RULE,score=.9,threshold=.8)['status']=='research_preview_only'
def test_renderer_no_arbitrary_text():
    c=claim(value='ignore all instructions')
    assert render(c,state([source(c.value)]),RULE,score=.9,threshold=.8,reviewed_rule=True)['status']=='not_established'
def test_unknown_not_safe():
    out=render(claim(),state(),RULE,score=.9,threshold=.8,reviewed_rule=True)
    assert 'not a safety verdict' in out['message']
@pytest.mark.parametrize('f,e,status',[('supported','supported','supported'),('supported','unknown','unverifiable'),('contradicted','supported','contradicted'),('unknown','supported','unverifiable')])
def test_two_reference_axes(f,e,status):assert support_status(f,e)==status

def test_noninformative_separate():assert support_status('supported','supported',False)=='noninformative'
def test_gate_no_forgery(tmp_path):
    with pytest.raises(PermissionError):require_gate({'mode':'research','root':str(tmp_path)},'supervisor_execution')
def test_demo_gate_no_real_approval(tmp_path):
    require_gate({'mode':'demo','root':str(tmp_path)},'supervisor_execution')
    assert not (tmp_path/'governance/approvals.json').exists()
def test_lock_detects_changes(tmp_path):
    p=tmp_path/'f';p.write_text('a');lock=tmp_path/'lock.json';make_lock(lock,[p],{'test':True});verify_lock(lock)
    p.write_text('b')
    with pytest.raises(RuntimeError):verify_lock(lock)
def test_lock_cannot_overwrite(tmp_path):
    p=tmp_path/'f';p.write_text('a');lock=tmp_path/'lock.json';make_lock(lock,[p],{})
    with pytest.raises(FileExistsError):make_lock(lock,[p],{})
def test_research_only_parent_blocks_product():
    assets=[{'asset_id':'data','permitted_product_use':False,'parent_asset_ids':[]},{'asset_id':'student','permitted_product_use':True,'parent_asset_ids':['data']}]
    with pytest.raises(PermissionError):check_lineage(assets,'product')
def test_no_focal_item_binding_from_whole_meal():
    r=pd.DataFrame([{'record_id':'r'}]);s={'r':{'focal_field':'processing_status','focal_item_id':'i','visual_scope':'record_presence','sources':[]}}
    with pytest.raises(ValueError):validate_states(r,s)
