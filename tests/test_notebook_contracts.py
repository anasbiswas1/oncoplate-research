import ast,importlib
from pathlib import Path
import pytest
import nbformat

REPO=Path(__file__).resolve().parents[1]


def test_all_notebook_imports_resolve():
    # Optional third-party models are imported lazily; checks every own-module name in notebook cells.
    for path in (REPO/'notebooks').glob('*.ipynb'):
        nb=nbformat.read(path,as_version=4);nbformat.validate(nb)
        for cell in nb.cells:
            if cell.cell_type!='code':continue
            tree=ast.parse(cell.source)
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith('oncoplate'):
                    module=importlib.import_module(node.module)
                    for alias in node.names:
                        assert hasattr(module,alias.name),f'{path.name}: missing {node.module}.{alias.name}'


def test_no_saved_notebook_outputs_or_credentials():
    for path in (REPO/'notebooks').glob('*.ipynb'):
        nb=nbformat.read(path,as_version=4)
        for cell in nb.cells:
            if cell.cell_type=='code':
                assert cell.execution_count is None and not cell.outputs
                assert 'ghp_' not in cell.source and 'github_pat_' not in cell.source


def test_principal_grid_is_sixty(tmp_path):
    from oncoplate.config import load_config
    from oncoplate.pipeline import grid_manifest
    cfg=load_config(REPO,root=tmp_path)
    df=grid_manifest(cfg);assert len(df)==60 and not df.run_id.duplicated().any()


def test_no_active_proxy_tiers_in_targets():
    for name in ('targets.py','training.py','pipeline.py','claims.py'):
        text=(REPO/'src/oncoplate'/name).read_text()
        assert 'PROTECTIVE' not in text and 'HIGH' not in text
