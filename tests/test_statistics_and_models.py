import numpy as np
import pandas as pd
import pytest
from oncoplate.statistics import *
from oncoplate.calibration import *
from oncoplate.selection import SoftLogistic,SoftMLP,validate_oof_ledger,choose_threshold
from oncoplate.io import write_json,read_json


def result_table(records):
    out=[]
    for method in ['M3','M7']:
        for seed in [0,1]:
            d=records.copy();d['method']=method;d['seed']=seed;d['accepted']=True;d['informative']=True
            d['support_status']=['contradicted' if (i%5==0 if method=='M3' else i%10==0) else 'supported' for i in range(len(d))];out.append(d)
    return pd.concat(out,ignore_index=True)

def test_domain_mixture(records):
    w=analysis_weights(records);assert np.isclose(w[records.domain=='meal'].sum(),.6)
def test_equal_groups_not_images(records):
    r=records.copy();extra=r.iloc[[0]].copy();extra.record_id='extra';r=pd.concat([r,extra],ignore_index=True)
    w=analysis_weights(r);tot=pd.DataFrame({'g':r.group_id,'d':r.domain,'w':w}).groupby(['g','d']).w.sum()
    assert np.isclose(tot.loc[('g0','meal')],tot.loc[('g1','meal')])
def test_missing_domain_not_renormalized(records):
    with pytest.raises(ValueError):analysis_weights(records[records.domain=='meal'])
def test_all_abstain_undefined_risk(records):
    r=result_table(records).query('method=="M3" and seed==0').copy();r.accepted=False
    m=assertion_metrics(r);assert np.isnan(m['unsupported_rate']) and m['coverage']==0

def test_bootstrap_paired_seed_average(records):
    out,rep=paired_bootstrap(result_table(records),B=30)
    assert out['risk_difference']<0

def test_missing_seed_rejected(records):
    r=result_table(records);r=r[~((r.method=='M7')&(r.seed==1))]
    with pytest.raises(ValueError):paired_bootstrap(r,B=30)
def test_different_cohort_rejected(records):
    r=result_table(records).iloc[1:]
    with pytest.raises(ValueError):paired_bootstrap(r,B=30)
def test_threshold_ties_not_split():
    x=choose_threshold([.9,.9,.5,.1],[True]*4,.5);assert x['validation_coverage']==.5

def test_unachievable_coverage_reported():
    x=choose_threshold([.9,.7,.4,.2],[True,False,False,False],.8);assert x['maximum_eligible_coverage']==.25

def test_no_eligible_claim_threshold():
    x=choose_threshold([.9,.8],[False,False],.8);assert x['validation_coverage']==0

def test_temperature_improves_objective():
    z=np.array([8.,8.,-8.,-8.]);y=np.array([1.,.7,0.,.3]);t=fit_temperature(z,y)
    assert bce_numpy(calibrated_logits(z,t),y)<=bce_numpy(z,y)+1e-6

def test_sigmoid_shapes():
    z=np.array([[1.,2.],[-1.,0.],[0.,1.]]);y=np.array([[1.,1.],[0.,0.],[.5,.5]])
    c=fit_sigmoid(z,y);assert probabilities(z,c).shape==z.shape

def test_soft_and_panel_brier():
    m=calibration_metrics(np.array([.5]),np.array([.5]));assert m['soft_brier']==0 and m['annotator_brier']==.25

def test_conformal_twenty_not_impossible():
    p=np.linspace(.51,.99,20);t=group_prediction_set_threshold(p,np.ones(20),np.arange(20),alpha=.05)
    assert np.isfinite(t['q'])
def test_conformal_small_finite_rank_abstains():
    t=group_prediction_set_threshold([.9],[1],['a'],alpha=.05);assert t['q']==float('inf')
    assert binary_support_sets([.1,.9],t).all()
def test_infinite_conformal_json_roundtrip(tmp_path):
    p=tmp_path/'q.json';write_json(p,{'q':float('inf')});assert binary_support_sets([.4],read_json(p)).all()

def test_selector_serialization(tmp_path):
    x=np.arange(30).reshape(10,3)/30;y=np.linspace(0,1,10)
    m=SoftLogistic().fit(x,y);p=tmp_path/'s.json';m.save(p,['a','b','c'],{})
    mm,f=SoftLogistic.load(p);assert np.allclose(m.predict(x),mm.predict(x))
def test_neural_selector_serialization(tmp_path):
    x=np.arange(30).reshape(10,3)/30;y=np.linspace(0,1,10)
    m=SoftMLP(epochs=3).fit(x,y);p=tmp_path/'m.json';m.save(p,['a','b','c'],{})
    mm,f=SoftMLP.load(p);assert np.allclose(m.predict(x),mm.predict(x))

def test_oof_leak_rejected():
    d=pd.DataFrame([dict(record_id='a',group_id='g',fold=0,training_group_ids='["g"]',early_stop_group_ids='[]',candidate_id='c',split='fit')])
    with pytest.raises(ValueError):validate_oof_ledger(d)
def test_oof_earlystop_leak_rejected():
    d=pd.DataFrame([dict(record_id='a',group_id='g',fold=0,training_group_ids='[]',early_stop_group_ids='["g"]',candidate_id='c',split='fit')])
    with pytest.raises(ValueError):validate_oof_ledger(d)
def test_holm_monotonic():
    a=holm_adjust([.001,.02,.8]);assert a[0]<=a[1]<=a[2]


def test_foundation_group_intervals_and_unassessable():
    from oncoplate.statistics import foundation_group_intervals
    import pandas as pd
    d=pd.DataFrame({'record_id':['a','b','c','d'],'group_id':['g1','g1','g2','g2'],
       'accepted':[True,True,True,False],'observed':[True,False,True,True],
       'agreement':[1.,float('nan'),0.,1.]})
    result,rep=foundation_group_intervals(d,B=100,seed=0)
    assert result['metrics']['answer_coverage_all_records']['estimate']==.75
    assert result['metrics']['assessable_answer_coverage']['estimate']==.5
    assert result['metrics']['panel_disagreement_among_assessable_answers']['estimate']==.5
    assert result['metrics']['unassessable_answer_coverage']['estimate']==.25
    assert len(rep)==100


def test_foundation_no_answer_has_undefined_risk():
    from oncoplate.statistics import foundation_group_intervals
    import pandas as pd
    import numpy as np
    d=pd.DataFrame({'record_id':['a','b'],'group_id':['g1','g2'],'accepted':[False,False],
       'observed':[True,True],'agreement':[1.,0.]})
    r,_=foundation_group_intervals(d,B=40)
    assert np.isnan(r['metrics']['panel_disagreement_among_assessable_answers']['estimate'])
    assert r['metrics']['panel_disagreement_among_assessable_answers']['ci95']==[None,None]
