from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from routes.user_auth import routes
from routes.user_operation import opt_routes

app = FastAPI()

app.include_router(routes, prefix="/api/v1")
app.include_router(opt_routes, prefix="/api/v1") 

@app.get("/")
async def root():
    return JSONResponse(content={
        "message":"I am Healthy."
    }, status_code=status.HTTP_200_OK)

