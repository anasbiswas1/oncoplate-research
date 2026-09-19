"""Soft-label calibration and explicit optional group-max prediction sets."""
from __future__ import annotations
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize,minimize_scalar


def bce_numpy(logits,y,mask=None):
    logits=np.asarray(logits,dtype=float);y=np.asarray(y,dtype=float)
    m=np.ones_like(y) if mask is None else np.asarray(mask,dtype=float)
    if m.sum()==0:return float("nan")
    return float(np.sum((np.logaddexp(0,logits)-y*logits)*m)/m.sum())


def fit_temperature(logits,y,mask=None):
    m=np.ones_like(y) if mask is None else np.asarray(mask)
    if m.sum()==0:raise ValueError("No calibration labels")
    result=minimize_scalar(lambda t:bce_numpy(np.asarray(logits)/np.exp(t),y,m),bounds=(-4,4),method="bounded")
    if not result.success:raise RuntimeError("Temperature optimisation failed")
    return {"kind":"temperature","temperature":float(np.exp(result.x)),"n_observed":int(m.sum())}


def fit_sigmoid(logits,y,mask=None,l2=.01):
    z=np.asarray(logits,dtype=float);y=np.asarray(y,dtype=float)
    if z.ndim==1:z=z[:,None];y=y[:,None]
    m=np.ones_like(y) if mask is None else np.asarray(mask,dtype=float).reshape(y.shape)
    scales=[];biases=[]
    for j in range(z.shape[1]):
        ok=m[:,j]>0
        if not ok.any():scales.append(1.0);biases.append(0.0);continue
        zz=z[ok,j];yy=y[ok,j]
        def objective(p):
            a,b=p;out=a*zz+b
            loss=np.mean(np.logaddexp(0,out)-yy*out)+.5*l2*((a-1)**2+b*b)
            e=expit(out)-yy
            return loss,np.array([np.mean(e*zz)+l2*(a-1),np.mean(e)+l2*b])
        res=minimize(objective,[1.0,0.0],jac=True,method="L-BFGS-B",bounds=[(0.01,20),(-20,20)])
        if not res.success:raise RuntimeError(f"Sigmoid calibration failed: {res.message}")
        scales.append(float(res.x[0]));biases.append(float(res.x[1]))
    return {"kind":"sigmoid","scale":scales,"bias":biases,"l2":l2}


def calibrated_logits(logits,cal):
    z=np.asarray(logits,dtype=float)
    if cal["kind"]=="temperature":return z/cal["temperature"]
    if cal["kind"]=="sigmoid":return z*np.asarray(cal["scale"])+np.asarray(cal["bias"])
    if cal["kind"]=="identity":return z
    raise ValueError("Unknown calibrator")


def probabilities(logits,cal=None):return expit(calibrated_logits(logits,cal or {"kind":"identity"}))


def calibration_metrics(p,y,mask=None,n_bins=15):
    p=np.asarray(p,float);y=np.asarray(y,float)
    m=np.ones_like(y,dtype=bool) if mask is None else np.asarray(mask)>0
    if not m.any():return {"n":0,"soft_brier":None,"annotator_brier":None,"log_loss":None,"ece":None}
    pp=p[m];yy=y[m]
    pp=np.clip(pp,1e-7,1-1e-7)
    soft=np.mean((pp-yy)**2)
    # Exact average Bernoulli Brier for an annotation panel with endorsement yy.
    panel=np.mean(yy*(1-pp)**2+(1-yy)*pp**2)
    bins=np.minimum((pp*n_bins).astype(int),n_bins-1);ece=0.;rows=[]
    for b in range(n_bins):
        ok=bins==b
        if ok.any():
            conf=float(pp[ok].mean());acc=float(yy[ok].mean());n=int(ok.sum())
            ece+=n/len(pp)*abs(conf-acc);rows.append({"bin":b,"n":n,"confidence":conf,"endorsement":acc})
    return {"n":int(m.sum()),"soft_brier":float(soft),"annotator_brier":float(panel),
            "log_loss":float(np.mean(-yy*np.log(pp)-(1-yy)*np.log1p(-pp))),"ece":float(ece),"bins":rows}


def group_prediction_set_threshold(p_supported,y_supported,groups,alpha=.1):
    """Optional binary-support prediction sets, using max nonconformity per group.
    Requires disjoint exchangeable calibration/new groups and fixed model/candidate rule.
    A singleton-supported set is NOT a certified selective error-rate bound.
    """
    p=np.asarray(p_supported,float);y=np.asarray(y_supported,int);groups=np.asarray(groups)
    if not np.isin(y,[0,1]).all():raise ValueError("Binary adjudicated support labels required")
    scores=np.where(y==1,1-p,p)
    maxima=np.array([scores[groups==g].max() for g in np.unique(groups)])
    k=int(np.ceil((len(maxima)+1)*(1-alpha)))
    if len(maxima)==0:raise ValueError("Empty group calibration set")
    q=float(np.sort(maxima)[k-1]) if k<=len(maxima) else float("inf")
    return {"q":q,"alpha":alpha,"groups":len(maxima),"scope":"group-marginal binary-support set; not selective-risk certification"}


def binary_support_sets(p,threshold):
    p=np.asarray(p,float);q=threshold["q"]
    if q is None:q=float("inf")
    include_unsupported=p<=q;include_supported=(1-p)<=q
    return np.column_stack([include_unsupported,include_supported])
