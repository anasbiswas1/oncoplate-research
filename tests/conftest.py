import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import pytest
import numpy as np
import pandas as pd

@pytest.fixture
def records():
    return pd.DataFrame([{"record_id":f"r{g}_{j}","group_id":f"g{g}","collection_group_id":f"g{g}",
                         "domain":["meal","product"][j],"sha256":f"hash_{g}_{j}"} for g in range(20) for j in range(2)])

@pytest.fixture
def reference_panel():
    return pd.DataFrame([
       {"record_id":"a","reviewer_id":"r1","item_id":"i1","category":"meat","subcategory":"chicken","cooking_style":"grilled"},
       {"record_id":"a","reviewer_id":"r1","item_id":"i2","category":"veg","subcategory":"potato","cooking_style":"boiled"},
       {"record_id":"a","reviewer_id":"r2","item_id":"i1","category":"meat","subcategory":"chicken","cooking_style":"fried"},
       {"record_id":"b","reviewer_id":"r1","item_id":"i1","category":"veg","subcategory":"unseen","cooking_style":""},
    ])
