from fastapi import FastAPI

from app.api.support import router as support_router

from app.core.exceptions import global_exception_handler

app = FastAPI(
    title="SmartHelp API",
    description="Micro-service de support client multimodal",
    version="1.0.0",
)

app.add_exception_handler(
    Exception,
    global_exception_handler
)

app.include_router(support_router)

