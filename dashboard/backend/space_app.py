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
one_launch) to fire spaces.zero.startup() (which calls client.
startup_report()) the first time .launch() runs. gr.mount_gradio_app()+
uvicorn.run() (the documented pattern for mounting Gradio into a custom
FastAPI app - needed so main.py's real routes stay reachable at their own
top-level paths, not nested under Gradio's UI) never calls .launch(), so
that hook never fired.

A prior attempt called .launch() on a throwaway port purely to trigger the
hook, then closed it - but HF Spaces' own proxy for Gradio SDK spaces
apparently also keys off that first .launch() call to decide which port to
route external traffic to, so it started routing to the now-closed
throwaway port instead of the real uvicorn server (/classify returned
404). Fix: call spaces.zero.startup() directly - the exact function
one_launch would have triggered - without ever calling .launch() at all,
so there's only ever one server (uvicorn on 7860) and nothing for the
platform's proxy to get confused about.
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
    from spaces.config import Config

    if Config.zero_gpu:
        from spaces.zero import startup as _zerogpu_startup

        _zerogpu_startup()

    uvicorn.run(app, host="0.0.0.0", port=7860)
