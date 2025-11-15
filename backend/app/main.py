from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import imports as imports_router, chat as chat_router, exports as exports_router

app = FastAPI(title="Sorftime 数据智能控制台 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(imports_router.router)
app.include_router(chat_router.router)
app.include_router(exports_router.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
