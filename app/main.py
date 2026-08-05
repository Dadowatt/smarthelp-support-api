from fastapi import FastAPI

from app.api.support import router as support_router

from app.core.exceptions import global_exception_handler

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SmartHelp API",
    description="Micro-service de support client multimodal",
    version="1.0.0",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(support_router)

