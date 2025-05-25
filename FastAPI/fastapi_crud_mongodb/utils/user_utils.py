from fastapi import HTTPException, status

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
    def is_email_exist(email:str):
        try:
            exist_user = Mongo.user_collection.find_one({
                "email":email
            })
            return exist_user is not None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while checking email: {str(e)}"
            )
    @staticmethod
    def check_confirm_password(password: str, confirm_password: str)->bool:
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password do not match."
            )
        return True
    
    @staticmethod
    def is_username_or_email_exist(user: str)->dict | None:
        try:
           exist_user = Mongo.user_collection.find_one({
                "$or":[
                    {"username":user},
                    {"email":user}
                ]
            })
           return exist_user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while checking username or email: {str(e)}"
            )
    

class UserOperation:
    @staticmethod
    def save_user_to_db(user:dict):
        try:
            result = Mongo.user_collection.insert_one(user)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while saving user data to the database: {str(e)}"
            )
