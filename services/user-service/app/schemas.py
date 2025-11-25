from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr
from pydantic.types import StringConstraints, SecretStr

# Password type: SecretStr (masked) with constraints
Password = Annotated[SecretStr, StringConstraints(min_length=8, max_length=72)]

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: Password

class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}
