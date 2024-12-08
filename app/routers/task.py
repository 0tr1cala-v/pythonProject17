from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, CreateUser, UpdateUser, UpdateTask
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    return task


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, new_task: CreateTask):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    else:
        db.execute(insert(Task).values(title=new_task.title,
                                       content=new_task.content,
                                       priority=new_task.priority,
                                       user_id=user_id,
                                       slug=slugify(new_task.title)))
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], updated_task: UpdateTask, task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        db.execute(update(Task).where(Task.id == task_id).values(title=updated_task.title,
                                                                 content=updated_task.content,
                                                                 priority=updated_task.priority))
        db.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'Task update is successful!'}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        db.execute(delete(Task).where(Task.id == task_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'Task deletion is successful!'}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )