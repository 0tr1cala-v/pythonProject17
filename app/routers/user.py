from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify


router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        db.scalars(select(Task).where(Task.user_id == user_id))
        return {"user_id": user.id, "tasks": [task for task in user.tasks]}
    else:
        raise HTTPException(status_code=404, detail='User was not found')


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    return user


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], new_user: CreateUser):
    try:
        db.execute(insert(User).values(username=new_user.username,
                                       firstname=new_user.firstname,
                                       lastname=new_user.lastname,
                                       age=new_user.age,
                                       slug=slugify(new_user.username)))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e)
                            )


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], updated_user: UpdateUser, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        db.execute(update(User).where(User.id == user_id).values(firstname=updated_user.firstname,
                                                                 lastname=updated_user.lastname,
                                                                 age=updated_user.age))
        db.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'User update is successful!'}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Task).where(Task.user_id == user_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'User deletion is successful!'}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )