"""HF Spaces entrypoint (Gradio SDK, free tier - Docker SDK strictly requires HF Pro).

Named space_app.py, not app.py, to avoid colliding with the app/ package
(app/main.py, app/pipeline.py, app/schemas.py) in this same directory.
Declared via `app_file: space_app.py` in README.md's YAML frontmatter.

ROOT CAUSE of the "[Errno 98] address already in use" crash loop hit by the
prior version of this file: it called gr.mount_gradio_app(fastapi_app, demo)
to get a combined ASGI app, then served that ourselves via uvicorn.run() -
bypassing demo.launch() entirely. Every diagnostic ruled out a bug in our
own code (only one uvicorn.run() call, no reload=, no workers=, no second
.launch() call anywhere) - the conflict was with something in HF's Gradio
SDK container infrastructure that expects .launch() to be the actual thing
that binds the port (confirmed by two *different* platform-level failures
across two hardware tiers: ZeroGPU's "No @spaces.GPU function detected",
then CPU Upgrade's port collision - both stemmed from never calling
.launch()).

FIX: work with the platform's expected pattern instead of around it. Gradio
Blocks() already exposes a real FastAPI instance at demo.app *before*
.launch() is even called (verified: gradio.routes.App is a FastAPI
subclass, supports include_router()/add_middleware() same as any other
FastAPI app). So instead of mounting Gradio into our app, merge our routes
+ CORS directly into Gradio's app, load models explicitly (since we're no
longer going through app.main's own FastAPI instance as the actual server,
its `lifespan` hook never fires), and let demo.launch() be the one and only
thing that starts a server.

Two follow-up findings from reading gradio/blocks.py + gradio/routes.py
directly (this app.include_router() call alone was NOT enough - verified
via a first attempt that got 404 on /health):
1. Blocks.launch() unconditionally rebuilds self.app from scratch via
   App.create_app(self, app=_app, ...) unless you pass its private
   (leading-underscore, undocumented but real) `_app` kwarg - without it,
   every route/middleware added to demo.app above gets silently discarded
   and replaced by a fresh App instance. Passing `_app=demo.app` makes
   create_app() reuse our modified instance instead (routes.py:373-381:
   `if app is None: app = App(...)  else: app.router.lifespan_context = ...`).
2. create_app() unconditionally adds its own CORS middleware
   (CustomCORSMiddleware) with strict_cors=True by default, which can
   override/conflict with our own CORSMiddleware added below - passing
   strict_cors=False to .launch() avoids that.

Even after both fixes above, the real deployed Space still 404'd on
/health/​/classify (served the Gradio SPA shell instead) - the actual
container log showed why: "Running on local URL: http://0.0.0.0:7860, with
SSR (Node proxy -> Python :7861)". Gradio 6.x's SSR mode puts a Node.js
front-end proxy in front of the Python backend; that proxy only forwards
paths it knows about (Gradio's own /gradio_api/* + static assets) and falls
back to serving the SPA shell for anything else, including our custom
top-level routes. `ssr_mode` defaults to None -> falls back to the
GRADIO_SSR_MODE env var (gradio/blocks.py) which HF's Gradio SDK base image
sets to enable SSR by default (it preinstalls Node 20+ for exactly this).
Passing ssr_mode=False overrides that and removes the Node proxy entirely -
Python's server becomes the only thing handling requests, at whatever port
we actually asked for.
"""
import sys
from pathlib import Path

import gradio as gr
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parent / "dashboard" / "backend"))

from app import pipeline  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402

with gr.Blocks() as demo:
    gr.Markdown(
        "CyberScope backend is running. API routes: `/classify`, `/explain`, "
        "`/health`. Interactive docs at `/docs`."
    )

demo.app.include_router(fastapi_app.router)
demo.app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app$",  # domain produksi + preview Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    pipeline.load_models()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        strict_cors=False,
        ssr_mode=False,
        _app=demo.app,
    )
