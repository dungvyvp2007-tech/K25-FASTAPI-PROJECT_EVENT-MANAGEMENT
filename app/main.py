from db.database import engine, Base
import models
from core.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from core.rate_limit import RateLimitMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from routers import auth, events, event_tasks, users
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="Event Management API")

Base.metadata.create_all(bind=engine)

app.add_middleware(RateLimitMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(event_tasks.router)


@app.get("/", tags=["System"])
def root():
    return {"message": "Event Management API đang hoạt động"}


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
