from passlib.context import CryptContext
from app.api.models.user import User, UserInDB
from app.api.db.dynamodb import get_dynamodb_resource

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self):
        self.dynamodb = get_dynamodb_resource()
        self.table = self.dynamodb.Table(
            "users"
        )  # Ensure the table 'users' exists in DynamoDB

    def get_user(self, username: str) -> UserInDB:
        response = self.table.get_item(Key={"username": username})
        if "Item" in response:
            return UserInDB(**response["Item"])
        return None

    def create_user(self, user: User) -> UserInDB:
        hashed_password = pwd_context.hash(user.password)
        user_in_db = UserInDB(username=user.username, hashed_password=hashed_password)
        self.table.put_item(Item=user_in_db.dict())
        return user_in_db

    def authenticate_user(self, user: User) -> UserInDB:
        db_user = self.get_user(user.username)
        if db_user and pwd_context.verify(user.password, db_user.hashed_password):
            return db_user
        return None

    def update_user(self, username: str, updated_data: dict) -> UserInDB:
        update_expression = "set " + ", ".join(f"{k}=:{k}" for k in updated_data.keys())
        expression_attribute_values = {f":{k}": v for k, v in updated_data.items()}
        response = self.table.update_item(
            Key={"username": username},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
        return UserInDB(**response["Attributes"])

    def delete_user(self, username: str) -> bool:
        self.table.delete_item(Key={"username": username})
        return True
