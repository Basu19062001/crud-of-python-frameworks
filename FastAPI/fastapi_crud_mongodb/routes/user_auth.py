from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from schemas.user_model import (
    UserModel,
    UserResponseModel,
    UserLoginModel,
    UserLoginResponse,
)
from utils.user_utils import UserAuthentication, UserOperation
from utils.security_utils import PasswordHashing, Token
from config import Mongo


routes = APIRouter(prefix="/user")

check_auth = OAuth2PasswordBearer(tokenUrl="/login")


@routes.post("/signup", response_model=UserResponseModel, tags=["User-Authentication"])
async def signup(user_data: UserModel):
    user_dict_data = user_data.model_dump()

    exist_username = UserAuthentication.is_username_exist(
        username=user_dict_data.get("username")
    )
    # if exist_username:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Username is already exist."
    #     )
    if exist_username:
        return JSONResponse(
            content={"message": "Username is already exist."},
            status_code=status.HTTP_409_CONFLICT,
        )

    exist_email = UserAuthentication.is_email_exist(email=user_dict_data.get("email"))

    if exist_email:
        return JSONResponse(
            content={"message": "User email is already exist."},
            status_code=status.HTTP_409_CONFLICT,
        )

    UserAuthentication.check_confirm_password(
        user_dict_data.get("password"), user_dict_data.get("confirm_password")
    )

    password = PasswordHashing.hashing_password(user_dict_data.get("password"))

    user_dict_data.update({"password": password})
    user_dict_data.pop("confirm_password", None)

    result = UserOperation.save_user_to_db(user_dict_data)

    resp_payload = {
        "id": str(result.inserted_id),
        "username": user_dict_data.get("username"),
        "email": user_dict_data.get("email"),
    }

    return JSONResponse(
        content={
            "message": "User login successful.",
            "status": True,
            "data": resp_payload,
        },
        status_code=status.HTTP_201_CREATED,
    )


@routes.post("/login", response_model=UserLoginResponse, tags=["User-Authentication"])
async def login(user: UserLoginModel):
    user_dict = user.model_dump()

    user = UserAuthentication.is_username_or_email_exist(
        user_dict.get("username_or_email")
    )
    # print(f"user-----:{user_dict.get("password")}")
    if user is None:
        return JSONResponse(
            content={"message": "Username or email doesn't exist."},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not PasswordHashing.verify_password(user_dict.get("password"), user["password"]):
        return JSONResponse(
            content={"message": "Invalid password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = Token.generate_token(user)

    try:
        Mongo.user_collection.update_one(
            {"username": user["username"]}, {"$set": {"access_token": access_token}}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while inserting access token to the database: {str(e)}",
        )

    return JSONResponse(
        content={
            "message": "login successful.",
            "status": True,
            "access_token": access_token,
        },
        status_code=status.HTTP_200_OK,
    )


@routes.post("/logout", tags=["User-Authentication"])
async def logout(token: str = Depends(check_auth)):
    try:
        user = Token.decode_token(token)
        if not user or "username" not in user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token",
            )

        username = user.get("username")
        Mongo.user_collection.update_one(
            {"username": username}, {"$unset": {"access_token": ""}}
        )

        return JSONResponse(
            content={"message": "Logout successful.", "status": True},
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while logout operation: {str(e)}",
        )
