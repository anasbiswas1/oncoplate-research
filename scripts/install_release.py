"""Standard-library-only, checksum-verified, non-overwriting release installation."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,shutil,stat,tempfile,zipfile
from datetime import datetime,timezone


def file_sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def install_release(archive,workspace,expected_sha256):
    archive=Path(archive).resolve();workspace=Path(workspace).resolve()
    if len(expected_sha256)!=64 or file_sha256(archive)!=expected_sha256:
        raise ValueError('Release ZIP checksum mismatch; use the matching installer and ZIP.')
    workspace.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        if not infos or len(infos)>10000:raise ValueError('Unexpected archive entry count')
        names=[i.filename for i in infos]
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP entries')
        for i in infos:
            p=PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0]!='oncoplate-research' or '\\' in i.filename:
                raise ValueError('Unsafe ZIP path')
            if stat.S_ISLNK(i.external_attr>>16):raise ValueError('ZIP symlinks are not permitted')
        total=sum(i.file_size for i in infos)
        if total>10*1024**3:raise ValueError('Unexpected release size; raw data and weights are not included')
        if total*2>shutil.disk_usage(workspace).free:raise OSError('Insufficient free space for safe staging')
        manifest=json.loads(z.read('oncoplate-research/RELEASE_MANIFEST.json'))
        declared={row['path']:row for row in manifest['files']}
        actual={str(PurePosixPath(i.filename).relative_to('oncoplate-research')) for i in infos if not i.is_dir()}
        if actual!=set(declared)|{'RELEASE_MANIFEST.json'}:raise ValueError('Release manifest does not match ZIP entries')
        with tempfile.TemporaryDirectory(prefix='.oncoplate-stage-',dir=workspace) as stage:
            z.extractall(stage)
            source=Path(stage)/'oncoplate-research'
            for rel,row in declared.items():
                path=source/rel
                if path.stat().st_size!=row['bytes'] or file_sha256(path)!=row['sha256']:
                    raise ValueError(f'File verification failed: {rel}')
            target=workspace/'oncoplate-research'
            if target.exists():target=workspace/f'oncoplate-research-v3.0.0-{stamp}'
            serial=1
            while target.exists():
                target=workspace/f'oncoplate-research-v3.0.0-{stamp}-{serial}';serial+=1
            shutil.move(str(source),str(target))
    pointer=workspace/'.oncoplate_install.json'
    if pointer.exists():
        backup=workspace/f'.oncoplate_install.previous-{stamp}.json';serial=1
        while backup.exists():backup=workspace/f'.oncoplate_install.previous-{stamp}-{serial}.json';serial+=1
        shutil.copy2(pointer,backup)
    metadata={'repository_path':str(target),'release_sha256':expected_sha256,'installed_at':stamp,
              'version':manifest['version'],'existing_checkouts_overwritten':False}
    fd,tmp=tempfile.mkstemp(prefix='.pointer-',suffix='.json',dir=workspace)
    try:
        with os.fdopen(fd,'w') as out:json.dump(metadata,out,indent=2)
        os.replace(tmp,pointer)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return metadata
