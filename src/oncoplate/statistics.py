"""Group-equal, domain-standardised, seed-separated empirical comparisons."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .io import require_columns,require_unique

VALID_STATUS={"supported","contradicted","unverifiable","noninformative","abstained"}


def bool_series(s):
    if s.dtype==bool:return s
    values=s.astype(str).str.lower()
    if not values.isin(["true","false","1","0"]).all():raise ValueError("Invalid boolean values")
    return values.isin(["true","1"])


def analysis_weights(df,mixture=None,multiplicities=None):
    mixture=mixture or {"meal":.6,"product":.4}
    if not np.isclose(sum(mixture.values()),1):raise ValueError("Mixture weights must sum to 1")
    require_unique(df,["record_id"])
    w=np.zeros(len(df),float);pos={idx:i for i,idx in enumerate(df.index)}
    for domain,share in mixture.items():
        sub=df[df.domain==domain]
        if sub.empty:raise ValueError(f"Domain {domain} absent; do not silently change registered mixture")
        counts=sub.groupby("group_id").size()
        mult={g:float(multiplicities.get(g,0)) if multiplicities is not None else 1. for g in counts.index}
        total=sum(mult.values())
        if total==0:raise ValueError("Bootstrap replicate has no groups in a registered domain")
        for idx,row in sub.iterrows():w[pos[idx]]=share*mult[row.group_id]/total/counts[row.group_id]
    if not np.isclose(w.sum(),1):raise ValueError("Weights do not cover all records/domains")
    return w


def assertion_metrics(df,mixture=None,multiplicities=None):
    require_columns(df,["record_id","group_id","domain","accepted","informative","support_status"])
    if not set(df.support_status).issubset(VALID_STATUS):raise ValueError("Unsupported rating vocabulary")
    w=analysis_weights(df,mixture,multiplicities)
    answered=bool_series(df.accepted).to_numpy() & bool_series(df.informative).to_numpy()
    if df.loc[answered,"support_status"].isin(["abstained","noninformative"]).any():raise ValueError("Answered focal claim lacks a valid rating")
    den=w[answered].sum();bad=df.support_status.isin(["contradicted","unverifiable"]).to_numpy()
    result={"unsupported_rate":float(w[answered&bad].sum()/den) if den>0 else np.nan,
       "coverage":float(den),"supported_yield":float(w[answered&~bad].sum()),
       "contradicted_rate":float(w[answered&df.support_status.eq("contradicted").to_numpy()].sum()/den) if den>0 else np.nan,
       "unverifiable_rate":float(w[answered&df.support_status.eq("unverifiable").to_numpy()].sum()/den) if den>0 else np.nan,
       "n_records":len(df),"n_groups":df.group_id.nunique(),"n_answered":int(answered.sum())}
    return result


def validate_paired_results(df,method_a,method_b,seeds=None):
    require_columns(df,["record_id","group_id","domain","method","seed","accepted","informative","support_status"])
    require_unique(df,["method","seed","record_id"])
    seeds=list(seeds if seeds is not None else sorted(df.seed.unique()))
    common=None
    for method in [method_a,method_b]:
        for seed in seeds:
            part=df[(df.method==method)&(df.seed==seed)]
            keys=set(zip(part.record_id,part.group_id,part.domain))
            if not keys:raise ValueError(f"Missing method/seed: {method}, {seed}")
            if common is None:common=keys
            elif keys!=common:raise ValueError("Methods/seeds do not share the same eligible evaluation cohort")
    return seeds


def paired_bootstrap(df,method_a="M7",method_b="M3",*,mixture=None,seeds=None,B=1000,seed=0,coverage_margin=.05):
    seeds=validate_paired_results(df,method_a,method_b,seeds)
    groups=np.array(sorted(df.group_id.unique()))
    def evaluate(mult=None):
        rr=[];cc=[];individual=[]
        for s in seeds:
            a=assertion_metrics(df[(df.method==method_a)&(df.seed==s)].copy(),mixture,mult)
            b=assertion_metrics(df[(df.method==method_b)&(df.seed==s)].copy(),mixture,mult)
            rr.append(a["unsupported_rate"]-b["unsupported_rate"]);cc.append(a["coverage"]-b["coverage"])
            individual.append({"seed":int(s),method_a:a,method_b:b})
        return float(np.mean(rr)),float(np.mean(cc)),individual
    point_r,point_c,per_seed=evaluate();rng=np.random.default_rng(seed);rep=[]
    for _ in range(B):
        sample=rng.choice(groups,len(groups),replace=True);g,n=np.unique(sample,return_counts=True)
        try:r,c,_=evaluate(dict(zip(g,n)))
        except ValueError:r,c=np.nan,np.nan
        rep.append([r,c])
    rep=np.asarray(rep);valid=np.isfinite(rep).all(1)
    enough=valid.sum()>=max(20,int(.8*B))
    rci=np.quantile(rep[valid,0],[.025,.975]).tolist() if enough else [None,None]
    cci=np.quantile(rep[valid,1],[.025,.975]).tolist() if enough else [None,None]
    return {"contrast":f"{method_a}-{method_b}","risk_difference":point_r,"coverage_difference":point_c,
      "risk_ci95":rci,"coverage_ci95":cci,"bootstrap_requested":B,"bootstrap_valid":int(valid.sum()),
      "success":bool(enough and rci[1]<0 and cci[0]>-coverage_margin),"coverage_margin":coverage_margin,
      "n_groups":len(groups),"per_seed":per_seed,"seed_dispersion_is_not_sampling_uncertainty":True,
      "interval_status":"ok" if enough else "insufficient_finite_replicates"},rep


def risk_coverage(df,score_col="score",eligible_col="eligible",mixture=None):
    w=analysis_weights(df,mixture);scores=df[score_col].to_numpy(float);eligible=bool_series(df[eligible_col]).to_numpy()
    bad=df.support_status.isin(["contradicted","unverifiable"]).to_numpy();rows=[]
    for threshold in np.unique(scores[eligible])[::-1]:
        answered=eligible&(scores>=threshold);coverage=w[answered].sum()
        rows.append({"threshold":threshold,"coverage":coverage,"unsupported_rate":w[answered&bad].sum()/coverage if coverage else np.nan})
    return pd.DataFrame(rows)


def holm_adjust(pvalues):
    p=np.asarray(pvalues,float)
    if not np.isfinite(p).all() or not ((0<=p)&(p<=1)).all():raise ValueError("Invalid p-values")
    order=np.argsort(p);adjusted=np.empty_like(p);current=0.
    for k,i in enumerate(order):current=max(current,(len(p)-k)*p[i]);adjusted[i]=min(current,1.)
    return adjusted


def pilot_precision(paired_group_differences,n_groups=(40,60,80,120),B=500,seed=0):
    """Empirical cluster resampling projection; not a claimed powered final design."""
    d=np.asarray(paired_group_differences,float)
    if len(d)<8 or not np.isfinite(d).all():raise ValueError("At least 8 usable paired pilot groups needed")
    rng=np.random.default_rng(seed);rows=[]
    for n in n_groups:
        means=rng.choice(d,size=(B,n),replace=True).mean(1)
        lo,hi=np.quantile(means,[.025,.975])
        rows.append({"groups":n,"projected_mean_difference":float(means.mean()),"empirical_ci_width":float(hi-lo),"pilot_groups":len(d),"bootstrap_replicates":B,"status":"planning_projection_not_power_validation"})
    return pd.DataFrame(rows)


def foundation_group_intervals(frame, *, B=1000, seed=0):
    """Participant-equal intervals for a *single* public-annotation model.

    Agreement is the panel endorsement fraction, not physical truth. Accepted
    predictions with missing reference masks remain in all-record coverage but
    are excluded from the explicitly assessable-disagreement denominator.
    """
    require_columns(frame, ['record_id','group_id','accepted','observed','agreement'])
    require_unique(frame,['record_id'])
    if B < 20: raise ValueError('At least 20 bootstrap replicates are needed')
    d=frame.copy();a=bool_series(d.accepted).to_numpy();o=bool_series(d.observed).to_numpy()
    q=d.agreement.to_numpy(float)
    if not np.isfinite(q[o]).all() or ((q[o]<0)|(q[o]>1)).any():
        raise ValueError('Observed agreement must be between zero and one')
    d['answer']=a.astype(float);d['assessable']=(a&o).astype(float)
    d['disagreement']=np.where(a&o,1-np.nan_to_num(q),0.)
    d['unassessable']=(a&~o).astype(float)
    g=d.groupby('group_id')[['answer','assessable','disagreement','unassessable']].mean()
    groups=g.to_numpy(float)
    def summary(means):
        risk=np.divide(means[...,2],means[...,1],out=np.full(means.shape[:-1],np.nan),where=means[...,1]>0)
        return np.stack([means[...,0],means[...,1],risk,means[...,3]],axis=-1)
    point=summary(groups.mean(0));rng=np.random.default_rng(seed)
    draws=rng.integers(0,len(g),size=(B,len(g)));rep=summary(groups[draws].mean(1))
    names=['answer_coverage_all_records','assessable_answer_coverage',
           'panel_disagreement_among_assessable_answers','unassessable_answer_coverage']
    out={'n_records':len(d),'n_groups':len(g),'bootstrap_requested':B,
         'reference':'expert_visual_panel_endorsement_not_documented_preparation','metrics':{}}
    for j,name in enumerate(names):
        good=np.isfinite(rep[:,j]);enough=len(g)>=2 and good.sum()>=max(20,int(.8*B))
        out['metrics'][name]={'estimate':float(point[j]),
            'ci95':np.quantile(rep[good,j],[.025,.975]).tolist() if enough else [None,None],
            'finite_replicates':int(good.sum()),'interval_status':'ok' if enough else 'insufficient_support'}
    return out,pd.DataFrame(rep,columns=names)
