import os
from oncoplate.api import create_app
import uvicorn
if __name__=='__main__':
    export=os.environ.get('ONCOPLATE_EXPORT_DIR')
    if not export:raise SystemExit('Set ONCOPLATE_EXPORT_DIR to a locally exported research checkpoint directory.')
    uvicorn.run(create_app(export),host='127.0.0.1',port=8000)
