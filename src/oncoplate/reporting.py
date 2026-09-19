from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from .io import read_json,write_json,write_table,sha256
from .calibration import calibration_metrics


def recognition_metrics(probs,y,mask,labels,threshold=.5):
    p=np.asarray(probs);y=np.asarray(y);m=np.asarray(mask)>0;pred=p>=threshold
    rows=[]
    # Primary tabular classification view uses panel-majority as an explicitly different endpoint.
    ref=y>.5
    for j,label in enumerate(labels):
        ok=m[:,j];tp=int((pred[:,j]&ref[:,j]&ok).sum());fp=int((pred[:,j]&~ref[:,j]&ok).sum());fn=int((~pred[:,j]&ref[:,j]&ok).sum())
        prec=tp/(tp+fp) if tp+fp else np.nan;rec=tp/(tp+fn) if tp+fn else np.nan
        f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else np.nan
        rows.append({"label":label,"n_observed":int(ok.sum()),"positive_majority_support":int((ref[:,j]&ok).sum()),"precision":prec,"recall":rec,"f1":f1})
    return pd.DataFrame(rows)


def plot_reliability(metric,path,title="Calibration against expert endorsement"):
    import matplotlib.pyplot as plt
    rows=metric["bins"]
    fig,ax=plt.subplots(figsize=(6,5));ax.plot([0,1],[0,1],linestyle="--",label="Identity")
    if rows:ax.plot([r["confidence"] for r in rows],[r["endorsement"] for r in rows],marker="o",label="Observed")
    ax.set(xlabel="Predicted probability",ylabel="Mean reference endorsement",title=title,xlim=(0,1),ylim=(0,1));ax.legend();fig.tight_layout()
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=200);plt.close(fig)


def plot_risk_coverage(curves,path):
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6.5,5))
    for method,df in curves.items():
        if len(df):ax.plot(df.coverage,df.unsupported_rate,label=method)
    ax.set(xlabel="Informative coverage",ylabel="Unsupported assertions among answers",xlim=(0,1));ax.legend();fig.tight_layout()
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=200);plt.close(fig)


def reproduce_index(root,output):
    root=Path(root);files=[]
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in (".csv",".json",".png",".svg") and p.resolve()!=Path(output).resolve():
            files.append({"path":str(p.relative_to(root)),"sha256":sha256(p),"bytes":p.stat().st_size})
    write_json(output,{"artifacts":files,"note":"Index of actual saved results; no missing tables or numbers are invented."})
    return files
