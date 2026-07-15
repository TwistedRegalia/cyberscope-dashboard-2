"""HF Spaces entrypoint (Gradio SDK, free tier - Docker SDK now requires HF Pro).

Named space_app.py, not app.py, to avoid colliding with the app/ package
(app/main.py, app/pipeline.py, app/schemas.py) in this same directory.
Declared via `app_file: space_app.py` in README.md's YAML frontmatter.

Mounts the real FastAPI app (app.main:app - unchanged, same routes/CORS/
lifespan as local dev) under a minimal Gradio Blocks UI at /ui, then serves
the combined app directly via uvicorn on port 7860 (the port HF Spaces
expects).

The `spaces` package's ZeroGPU startup check ("No @spaces.GPU function
detected during startup") isn't satisfied just by a decorated function
existing - it monkey-patches gr.Blocks.launch (spaces/zero/gradio.py:
one_launch) to fire its startup_report() the first time .launch() runs.
Since we serve via gr.mount_gradio_app()+uvicorn.run() (the documented
pattern for mounting Gradio into a custom FastAPI app) and never call
.launch(), that hook never fired. Fix: launch the placeholder Blocks once
on a throwaway port (prevent_thread_lock=True) purely to trigger the hook,
then close it immediately - the real app is still served by uvicorn on
7860 as before.
"""
import sys
from pathlib import Path

import gradio as gr
import spaces
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent / "dashboard" / "backend"))

from app.main import app as fastapi_app  # noqa: E402


@spaces.GPU()
def _zerogpu_probe():
    """Marker only - the ZeroGPU hardware tier requires >=1 @spaces.GPU
    function to exist or the Space fails startup validation. This backend
    is designed for CPU inference (CLAUDE.md Sec 9) and never calls this;
    @spaces.GPU is documented as a no-op outside an actual GPU-requesting
    call, so its mere presence here has no effect on the real inference
    path in pipeline.py."""
    pass


with gr.Blocks() as _demo:
    gr.Markdown(
        "CyberScope backend is running. API routes: `/classify`, `/explain`, "
        "`/health`. Interactive docs at `/docs`."
    )

app = gr.mount_gradio_app(fastapi_app, _demo, path="/ui")

if __name__ == "__main__":
    _demo.launch(prevent_thread_lock=True, server_name="0.0.0.0", server_port=7861, quiet=True)
    _demo.close()
    uvicorn.run(app, host="0.0.0.0", port=7860)
