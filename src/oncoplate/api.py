"""Local research-only visual-prediction API. No arbitrary client-asserted verified sources."""
from pathlib import Path
import io,json,uuid
import numpy as np
import torch
from PIL import Image,UnidentifiedImageError
from .io import read_json,sha256
from .vision import Letterbox


def create_app(export_dir):
    from fastapi import FastAPI,UploadFile,File,HTTPException
    root=Path(export_dir);contract=read_json(root/'export_contract.json')
    model_path=root/'predictor.torchscript.pt'
    if sha256(model_path)!=contract['files']['torchscript']:raise ValueError('Export hash mismatch')
    model=torch.jit.load(str(model_path),map_location='cpu').eval()
    labels=[json.loads(l) for l in contract['target_schema']['labels']]
    app=FastAPI(title='OncoPlate local research prototype',version='3.0.0',description='Qualified visual attributes only; no cancer-risk probability or chemical measurement.')
    @app.get('/health')
    def health():return {'status':'ready','research_only':True,'clinical_validation':False,'model_sha256':contract['files']['torchscript']}
    @app.post('/research/predict')
    async def predict(image:UploadFile=File(...)):
        data=await image.read(10*1024*1024+1)
        if len(data)>10*1024*1024:raise HTTPException(413,'Image exceeds 10 MiB research limit')
        try:
            with Image.open(io.BytesIO(data)) as im:
                if im.width*im.height>25_000_000:raise HTTPException(413,'Image dimensions exceed research limit')
                x=Letterbox(contract['image_size'])(im).unsqueeze(0)
        except (UnidentifiedImageError,OSError,Image.DecompressionBombError):raise HTTPException(400,'Unreadable image')
        with torch.inference_mode():p=model(x).numpy().ravel()
        top=np.argsort(-p)[:min(3,len(p))]
        return {'request_id':str(uuid.uuid4()),'research_only':True,'retained_image':False,
                'output_scope':'record_presence_visual_predictions_not_item_confirmations',
                'probability_target':'visual_annotation_endorsement_not_claim_support_or_cancer_risk',
                'predictions':[{'qualifier':'model_prediction','attributes':labels[j],'probability':float(p[j])} for j in top],
                'notice':'The image alone may not establish ingredients or processing. No chemical measurement or food-safety verdict is provided.'}
    static=Path(__file__).resolve().parents[2]/"app/static"
    if static.exists():
        from fastapi.staticfiles import StaticFiles
        app.mount("/",StaticFiles(directory=str(static),html=True),name="research_preview")
    return app
