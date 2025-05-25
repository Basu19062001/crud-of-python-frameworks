from datetime import datetime, timezone
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

from config import Mongo


class UserAuthentication:
    @staticmethod
    def is_username_exist(username: str):
        try:
            exist_user = Mongo.user_collection.find_one({"username": username})
            return exist_user is not None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while checking username: {str(e)}",
            )

    @staticmethod
    def is_email_exist(email: str):
        try:
            exist_user = Mongo.user_collection.find_one({"email": email})
            return exist_user is not None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while checking email: {str(e)}",
            )

    @staticmethod
    def check_confirm_password(password: str, confirm_password: str) -> bool:
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password do not match.",
            )
        return True

    @staticmethod
    def is_username_or_email_exist(user: str) -> dict | None:
        try:
            exist_user = Mongo.user_collection.find_one(
                {"$or": [{"username": user}, {"email": user}]}
            )
            return exist_user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while checking username or email: {str(e)}",
            )


class UserOperation:

    @staticmethod
    def get_obj_id(user_id: str) -> ObjectId:
        try:
            return ObjectId(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error while converting the Id to objectId: {str(e)}",
            )

    @staticmethod
    def save_user_to_db(user: dict):
        try:
            result = Mongo.user_collection.insert_one(user)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while saving user data to the database: {str(e)}",
            )

    @classmethod
    def get_user_by_id(cls, user_id: str) -> dict:
        try:
            _id = cls.get_obj_id(user_id)
            pipeline = [
                {"$match": {"_id": _id, "is_delete": False}},
                {
                    "$project": {
                        "_id": 0,
                        "updated_at": 0,
                        "is_delete": 0,
                    }
                },
            ]

            result = Mongo.user_collection.aggregate(pipeline)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
                )

            return result[0]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while find user data from the database: {str(e)}",
            )

    @classmethod
    def update_user_by_id(cls, user_id: str, user_data: dict):
        try:
            _id = cls.get_obj_id(user_id)

            user = Mongo.user_collection.find_one({"_id": _id, "is_delete": False})

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found or has been deleted",
                )

            update_fields = {
                key: value for key, value in user_data.items() if value is not None
            }

            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid fields provided for update",
                )

            Mongo.user_collection.update_one(
                {
                    "_id": _id,
                },
                {"$set": {**update_fields, "updated_at": datetime.now(timezone.utc)}},
            )

            return JSONResponse(
                content={"message": "User updated successfully", "status": True},
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while update user data to the database: {str(e)}",
            )
