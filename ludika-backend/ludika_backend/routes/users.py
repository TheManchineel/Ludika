from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Security
from sqlmodel import Session, select
from uuid import UUID

from ludika_backend.controllers.auth import get_current_user, hash_password
from ludika_backend.models.users import (
    User,
    UserPublic,
    UserUpdateVisibleName,
    UserUpdatePassword,
    UserAdminUpdate,
    UserRole,
)
from ludika_backend.utils.db import get_session

user_router = APIRouter()


@user_router.get("/")
async def list_users(
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> list[UserPublic]:
    if not current_user.is_privileged():
        raise HTTPException(
            status_code=403, detail="You do not have permission to view users."
        )
    users = db_session.exec(select(User)).all()
    return users


@user_router.patch("/me/visible-name")
async def update_visible_name(
    update: UserUpdateVisibleName,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> UserPublic:
    current_user.visible_name = update.visible_name
    db_session.add(current_user)
    db_session.commit()
    db_session.refresh(current_user)
    return current_user


@user_router.patch("/me/password")
async def update_password(
    update: UserUpdatePassword,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> UserPublic:
    current_user.password_hash = hash_password(update.password.get_secret_value())
    db_session.add(current_user)
    db_session.commit()
    db_session.refresh(current_user)
    return current_user


@user_router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> UserPublic:
    if not current_user.is_privileged():
        raise HTTPException(
            status_code=403, detail="You do not have permission to view users."
        )
    user = db_session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@user_router.patch("/{user_id}")
async def admin_update_user(
    user_id: UUID,
    update: UserAdminUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> UserPublic:
    if not current_user.is_privileged():
        raise HTTPException(
            status_code=403, detail="You do not have permission to update users."
        )
    user = db_session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if update.enabled is not None:
        user.enabled = update.enabled
    if update.user_role is not None:
        if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
            raise HTTPException(
                status_code=403, detail="Only admins can change user roles."
            )
        user.user_role = update.user_role
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(status_code=403, detail="Only admins can delete users.")
    user = db_session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db_session.delete(user)
    db_session.commit()
    return {"detail": "User deleted."}
