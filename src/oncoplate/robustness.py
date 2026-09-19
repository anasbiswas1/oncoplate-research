from __future__ import annotations
import copy,itertools
import numpy as np
from PIL import Image,ImageEnhance,ImageFilter
from .claims import eligibility


def image_variants(image):
    im=image.convert("RGB")
    return {"original":im,"brightness_low":ImageEnhance.Brightness(im).enhance(.8),"brightness_high":ImageEnhance.Brightness(im).enhance(1.2),"blur":im.filter(ImageFilter.GaussianBlur(1.))}


def tuple_swaps(items):
    """Swap preparation reports while keeping marginal names; not physical counterfactuals."""
    output=[]
    for i,j in itertools.combinations(range(len(items)),2):
        if items[i].get("cooking_style")==items[j].get("cooking_style"):continue
        swapped=copy.deepcopy(items)
        swapped[i]["cooking_style"],swapped[j]["cooking_style"]=swapped[j]["cooking_style"],swapped[i]["cooking_style"]
        output.append(swapped)
    return output


def monotonicity_check(claims,full_state,less_informed_state,rules):
    full={c.candidate_id for c in claims if c.qualifier!="predicted" and eligibility(c,full_state,rules[c.field])[0]}
    reduced={c.candidate_id for c in claims if c.qualifier!="predicted" and eligibility(c,less_informed_state,rules[c.field])[0]}
    return {"pass":reduced.issubset(full),"gained_after_information_deletion":sorted(reduced-full),
            "scope":"fixed predicates/candidates and deterministic completion gate; not a guarantee for recomputed learned outputs"}


def image_perturbations(image_path,output):
    from pathlib import Path
    from .io import write_json,sha256
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with Image.open(image_path) as im:variants=image_variants(im)
    manifest=[]
    for name,im in variants.items():
        path=out/f'{name}.png';im.save(path);manifest.append({'variant':name,'path':str(path),'sha256':sha256(path),'scope':'appearance_only_preserve_items'})
    write_json(out/'manifest.json',manifest);return manifest
