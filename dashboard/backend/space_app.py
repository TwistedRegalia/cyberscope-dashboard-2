"""HF Spaces entrypoint (Gradio SDK, free tier - Docker SDK now requires HF Pro).

Named space_app.py, not app.py, to avoid colliding with the app/ package
(app/main.py, app/pipeline.py, app/schemas.py) in this same directory.
Declared via `app_file: space_app.py` in README.md's YAML frontmatter.

Mounts the real FastAPI app (app.main:app - unchanged, same routes/CORS/
lifespan as local dev) under a minimal Gradio Blocks UI at /ui, then serves
the combined app directly via uvicorn on port 7860 (the port HF Spaces
expects). The Gradio SDK doesn't require calling demo.launch() - it just
runs this script and expects something bound to port 7860 when it's done
starting up; the Gradio mount is a safety net for whatever SDK-specific
checks Spaces may run, not strictly required for the API routes themselves.
"""
import gradio as gr
import uvicorn

from app.main import app as fastapi_app

with gr.Blocks() as _demo:
    gr.Markdown(
        "CyberScope backend is running. API routes: `/classify`, `/explain`, "
        "`/health`. Interactive docs at `/docs`."
    )

app = gr.mount_gradio_app(fastapi_app, _demo, path="/ui")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
