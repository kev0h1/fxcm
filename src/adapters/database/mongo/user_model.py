from mongoengine import *
from src.domain.user import User


class UserModel(Document):
    def __init__(
        self, id, name, email, password, position_size, *args, **values
    ):
        super().__init__(*args, **values)
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.position_size = position_size

    id = StringField(primary_key=True)
    name = StringField()
    email = StringField()
    password = StringField()
    position_size = DecimalField()


async def map_to_db_model(user: User):
    """Maps trade domain model to database model

    Args:
        trade (Trade): trade domain model

    Returns:
        Trade: database model
    """
    if not user:
        return None
    return UserModel(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        position_size=user.position_size,
    )


async def map_to_domain_model(user: UserModel):
    """Maps trade database model to domain model

    Args:
        trade (Trade): trade database model

    Returns:
        Trade: domain model
    """
    if not user:
        return None
    return User(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        position_size=user.position_size,
    )
