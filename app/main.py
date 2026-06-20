from fastapi import FastAPI

from app.routes.detect import router as detect_router
from app.routes.health import router as health_router


app = FastAPI(
    title="ARGUS IC Backend",
    description="API experimental para deteccao, profundidade monocular relativa e feedback auditivo.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(detect_router)
