from sqladmin import ModelView

from src.auth.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.superuser, User.active]
