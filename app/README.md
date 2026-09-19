# Local research prototype

After notebook 15, use notebook 25 for an in-process API test, or:

```bash
pip install -e '.[app]'
export ONCOPLATE_EXPORT_DIR=/absolute/path/to/your/exports/run_id
python app/serve.py
```

The server binds to **127.0.0.1:8000** only. Open that address to use the supplied mobile-responsive research preview. It is a local web prototype, not a native app. It accepts `POST /research/predict` with a multipart image and returns qualified visual annotation predictions. It does not persist uploaded images. `/health` reports the model hash and research-only status.

This is an integration aid, not a complete native app or a public medical service. Do not expose it through a public tunnel. Authentication, consent, server-side source verification, a reviewed PCSI service, incident handling, device evaluation and release decisions remain separate work.
