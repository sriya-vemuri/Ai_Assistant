from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import upload, query

app = FastAPI(
    title="Private QA Assistant",
    version="0.1.0",
    openapi_version="3.1.0",
)

# serve /app/reports as /reports
app.mount("/reports", StaticFiles(directory="app/reports"), name="reports")

# your existing routers
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(query.router, prefix="/query", tags=["query"])

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")
