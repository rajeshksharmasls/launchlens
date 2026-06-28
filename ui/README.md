# LaunchLens UI

Static frontend for the LaunchLens market-launch workbench.

Open [index.html](./index.html) directly in a browser. The UI tries to call the API URL shown in the sidebar and falls back to mock-mode responses when the API is unavailable.

To use it with the optional FastAPI server:

```bash
python -m pip install -e ".[api]"
uvicorn api.app:app --reload
```

Then keep the UI API URL as `http://127.0.0.1:8000/chat`.
