from typing import List, Optional
from ..schemas.users import UserCreate, UserUpdate, UserResponse, User

class UserService:
    def __init__(self):
        self.users = []
        self._id_counter = 1

    def create_user(self, user_in: UserCreate) -> User:
        user = User(
            id=self._id_counter,
            username=user_in.username
        )
        # In a real app, we would hash the password here
        # user_data = user_in.model_dump()
        # user_data["id"] = self._id_counter
        self.users.append({"id": self._id_counter, "username": user_in.username, "password": user_in.password})
        self._id_counter += 1
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        for u in self.users:
            if u["id"] == user_id:
                return User(id=u["id"], username=u["username"])
        return None

    def get_users(self) -> List[User]:
        return [User(id=u["id"], username=u["username"]) for u in self.users]

    def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        for u in self.users:
            if u["id"] == user_id:
                if user_in.username:
                    u["username"] = user_in.username
                if user_in.password:
                    u["password"] = user_in.password
                return User(id=u["id"], username=u["username"])
        return None

    def delete_user(self, user_id: int) -> bool:
        for i, u in enumerate(self.users):
            if u["id"] == user_id:
                self.users.pop(i)
                return True
        return False

user_service = UserService()
