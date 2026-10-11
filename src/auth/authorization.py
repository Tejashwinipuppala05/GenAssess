from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status

from .models import User, UserRole
from .routes import get_current_user


def require_role(required_role: UserRole) -> Callable[..., User]:
    def role_guard(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this area.",
            )
        return user

    return role_guard
