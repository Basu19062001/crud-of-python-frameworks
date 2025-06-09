from typing import Optional
from fastapi import APIRouter, HTTPException, status, Path, Depends, Query
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

from routes.user_auth import check_auth
from utils.security_utils import Token, PasswordHashing
from utils.user_utils import UserOperation
from config import Mongo
from schemas.user_model import UserUpdateModel

opt_routes = APIRouter(prefix="/user")


@opt_routes.get("/get_users", tags=["User-Operation"])
async def get_users(
    token: str = Depends(check_auth),
    page: int = Query(1, ge=1, description="Page number [starting from 1]"),
    limit: int = Query(5, ge=1, le=100, description="Users per page [max 100]"),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    try:
        user = Token.decode_token(token=token)
        skip = (page - 1) * limit
        filters = []

        if username:
            filters.append({"username": {"$regex": username, "$options": "i"}})

        if email:
            filters.append({"email": {"$regex": email, "$options": "i"}})

        match_stage = {"$match": {"$and": filters}} if filters else {"$match": {}}

        pipeline = [
            match_stage,
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$project": {
                    "_id": {"$toString": "&_id"},
                    "username": 1,
                    "email": 1,
                    "created_at": 1,
                }
            },
        ]

        user_cursor = Mongo.user_collection.aggregate(pipeline)
        users = list(user_cursor)

        total_count = Mongo.user_collection.count_documents(match_stage.get("$match"))

        return JSONResponse(
            content={
                "message": "Users fetched successfully.",
                "status": True,
                "pagination": {
                    "total": total_count,
                    "page": page,
                    "limit": limit,
                    "total_pages": (total_count + limit - 1) // limit,
                },
                "data": users,
            }
        )
    except PyMongoError as pe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(pe)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@opt_routes.get("/get-user/{user_id}", tags=["User-Operation"])
async def get_user_by_id(token: str = Depends(check_auth), user_id: str = Path(...)):
    try:
        token_user = Token.decode_token(token)
        user = UserOperation.get_user_by_id(user_id)
        if not user:
            return JSONResponse(
                content={"message": "User not found", "status": False},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return JSONResponse(
            content={"message": "User found", "status": True, "user": user},
            status_code=status.HTTP_200_OK,
        )
    except PyMongoError as pe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while searching user to the database: {str(pe)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred: {str(e)}",
        )


@opt_routes.patch("/user-update/{user_id}", tags=["User-Operation"])
async def user_update_by_id(
    token: str = Depends(check_auth),
    user_id: str = Path(..., description="ID of the user to update"),
    user_data: UserUpdateModel = None,
):
    try:
        token_user = Token.decode_token(token)
        user_dict = user_data.model_dump()

        password = user_dict.get("password")
        confirm_password = user_dict.get("password")

        if password or confirm_password:
            if password != user_dict.get("confirm_password"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password do not match",
                )

        hashed_password = PasswordHashing.hashing_password(user_dict.get("password"))
        user_dict["password"] = hashed_password

        user_dict.pop("confirm_password", None)

        UserOperation.update_user_by_id(user_id=user_id, user_data=user_dict)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while update user by id: {str(e)}",
        )


@opt_routes.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK, tags=["User-Operation"])
async def delete_user_by_id(
    token: str = Depends(check_auth),
    user_id: str = Path(..., description="Id of the user to delete"),
    ):
    pass