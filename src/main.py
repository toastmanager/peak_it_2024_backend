from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqladmin import Admin

from src.auth.admin import UserAdmin
from src.auth.dependencies import get_auth_service
from src.auth.router import auth_router
# from src.media.router import router as media_router
from src.auth.utils import jwt_decode
from src.core.database import engine
from src.core.config import settings

app = FastAPI(dependencies=[Depends(get_auth_service)])

origins = ["http://localhost", "http://localhost:8080", settings.host]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_v1 = FastAPI(title="FastAPI Boilerplate v1")
admin_v1 = Admin(app=app_v1, engine=engine)


@app.middleware("http")
async def check_authentication(request: Request, call_next):
    url = request.url.path.split("/")
    if len(url) >= 4 and url[3] == "admin":
        token = request.headers.get("Authorization")
        payload = {}
        try:
            if not token:
                return JSONResponse(
                    status_code=401, content={"message": "Token is not provided"}
                )
            payload = jwt_decode(token)
        except Exception:
            return JSONResponse(status_code=401, content={"message": "Invalid token"})
        superuser = payload.get("superuser", False)
        if not superuser:
            return JSONResponse(status_code=401, content={"message": "Not superuser"})
    response = await call_next(request)
    return response


app_v1.include_router(auth_router)
# app_v1.include_router(media_router, prefix="/media")
admin_v1.add_view(UserAdmin)

app.mount("/api/v1", app_v1)
