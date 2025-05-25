from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from routes.user_auth import routes

app = FastAPI()

app.include_router(routes, prefix="/api/v1")

@app.get("/")
async def root():
    return JSONResponse(content={
        "message":"I am Healthy."
    }, status_code=status.HTTP_200_OK)

