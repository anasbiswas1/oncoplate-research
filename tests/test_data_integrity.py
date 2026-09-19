import json,zipfile
import numpy as np
import pandas as pd
import pytest
from oncoplate.splits import build_components,grouped_split,validate_split,save_split
from oncoplate.targets import build_schema,make_targets,label_key,marginal_tuple_score
from oncoplate.downloads import extract_zip
from oncoplate.datasets import values,normalize
from oncoplate.io import digest,write_json,read_json,atomic_npz


def test_groups_never_cross(records):
    r=grouped_split(records);assert r.groupby('group_id').split.nunique().max()==1
    assert set(r.split)=={'fit','validation','calibration','test'}

def test_fixed_seed(records):
    assert grouped_split(records).equals(grouped_split(records))

def test_split_seed_changes(records):
    assert not grouped_split(records,seed=0).equals(grouped_split(records,seed=1))

def test_duplicate_links_groups(records):
    records.loc[2,'sha256']=records.loc[0,'sha256'];r=build_components(records)
    assert r.loc[0,'group_id']==r.loc[2,'group_id']

def test_false_edge_not_approved(records):
    e=pd.DataFrame([{'record_a':'r0_0','record_b':'r1_0','approved':'False'}])
    r=build_components(records,e);assert r.loc[0,'group_id']!=r.loc[2,'group_id']

def test_true_edge_approved(records):
    e=pd.DataFrame([{'record_a':'r0_0','record_b':'r1_0','approved':'True'}])
    r=build_components(records,e);assert r.loc[0,'group_id']==r.loc[2,'group_id']

def test_generic_domain_not_group_edge(records):
    r=build_components(records);assert r.group_id.nunique()==20

def test_empty_identifier_not_edge(records):
    records['household_pseudonym']='';assert build_components(records).group_id.nunique()==20

def test_split_overwrite_refused(records,tmp_path):
    save_split(grouped_split(records),tmp_path)
    with pytest.raises(RuntimeError):save_split(grouped_split(records,seed=1),tmp_path)

def test_tampered_split(records):
    r=grouped_split(records);r.loc[0,'split']='fit';r.loc[1,'split']='test'
    with pytest.raises(ValueError):validate_split(r)

def test_fit_only_vocabulary(reference_panel):
    schema=build_schema(reference_panel,['a'],'independent',['subcategory'])
    assert all('unseen' not in x for x in schema['labels'])

def test_no_cross_item_tuple(reference_panel):
    schema=build_schema(reference_panel,['a'],'joint',['category','subcategory','cooking_style'])
    assert not any('chicken' in x and 'boiled' in x for x in schema['labels'])

def test_annotator_fraction(reference_panel):
    schema=build_schema(reference_panel,['a'],'joint',['category','subcategory','cooking_style'])
    targets=make_targets(pd.DataFrame({'record_id':['a','b']}),reference_panel,schema)
    i=next(i for i,v in enumerate(schema['labels']) if 'chicken' in v and 'grilled' in v)
    assert targets['y'][0,i]==.5

def test_missing_method_mask(reference_panel):
    schema=build_schema(reference_panel,['a'],'joint',['category','subcategory','cooking_style'])
    t=make_targets(pd.DataFrame({'record_id':['a','b']}),reference_panel,schema)
    assert t['mask'][1].sum()==0

def test_unseen_recorded(reference_panel):
    schema=build_schema(reference_panel,['a'],'independent',['subcategory'])
    t=make_targets(pd.DataFrame({'record_id':['a','b']}),reference_panel,schema)
    assert len(t['unseen'])==1

@pytest.mark.parametrize('input,expected',[(None,''),(' UNKNOWN ',''),('none','none'),('Pan  Fried','pan fried')])
def test_normalize(input,expected):assert normalize(input)==expected

def test_no_comma_split():assert values('rice, beans')==['rice, beans']

def test_explicit_list():assert values('["a","b"]')==['a','b']

def test_zip_traversal(tmp_path):
    p=tmp_path/'bad.zip'
    with zipfile.ZipFile(p,'w') as z:z.writestr('../bad.txt','x')
    with pytest.raises(ValueError):extract_zip(p,tmp_path/'out')

def test_zip_good(tmp_path):
    p=tmp_path/'good.zip'
    with zipfile.ZipFile(p,'w') as z:z.writestr('sub/a.txt','okay')
    extract_zip(p,tmp_path/'out');assert (tmp_path/'out/sub/a.txt').read_text()=='okay'

def test_atomic_npz(tmp_path):
    p=tmp_path/'a.npz';atomic_npz(p,x=np.array([1,2]));assert np.load(p)['x'].tolist()==[1,2]

def test_json_nan_is_null(tmp_path):
    p=tmp_path/'a.json';write_json(p,{'a':float('nan')});assert read_json(p)['a'] is None
