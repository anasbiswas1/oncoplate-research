import importlib.util,json,zipfile,hashlib
from pathlib import Path
import pytest
script=Path(__file__).resolve().parents[1]/'scripts/install_release.py'
spec=importlib.util.spec_from_file_location('release_installer',script)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def archive(tmp_path):
    data=b'test software only\n';sha=hashlib.sha256(data).hexdigest()
    manifest={'version':'3.0.0','files':[{'path':'README.md','bytes':len(data),'sha256':sha}]}
    path=tmp_path/'release.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('oncoplate-research/README.md',data)
        z.writestr('oncoplate-research/RELEASE_MANIFEST.json',json.dumps(manifest))
    return path


def test_installer_preserves_existing_checkout(tmp_path):
    z=archive(tmp_path);root=tmp_path/'drive';old=root/'oncoplate-research';old.mkdir(parents=True)
    (old/'owned.txt').write_text('must stay');result=module.install_release(z,root,module.file_sha256(z))
    assert (old/'owned.txt').read_text()=='must stay'
    assert Path(result['repository_path'])!=old and not result['existing_checkouts_overwritten']
    assert (root/'.oncoplate_install.json').exists()


def test_installer_rejects_hash_mismatch(tmp_path):
    z=archive(tmp_path)
    with pytest.raises(ValueError,match='checksum'):module.install_release(z,tmp_path/'drive','0'*64)


def test_installer_rejects_zip_slip(tmp_path):
    z=archive(tmp_path)
    with zipfile.ZipFile(z,'a') as out:out.writestr('oncoplate-research/../../escape.txt','bad')
    with pytest.raises(ValueError,match='Unsafe'):module.install_release(z,tmp_path/'drive',module.file_sha256(z))
