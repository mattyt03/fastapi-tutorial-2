from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List


router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get('/', response_model=List[schemas.PostResponseWithLikes])
# the search parameter is optional but we provide a default?
def get_posts(db: Session = Depends(get_db), user=Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: str = ''):
    # by default, sqlalchemy performs left inner joins
    # i thought outer joins only included posts without likes?
    join_operation = db.query(models.Post, func.count(models.Like.post_id).label('likes')).join(
        models.Like, models.Post.id == models.Like.post_id, isouter=True).group_by(models.Post.id)
    # apply query params and return result
    posts = join_operation.filter(models.Post.title.contains(search)).order_by(
        models.Post.created_at).limit(limit).offset(skip).all()
    # query for retrieving only the user's posts
    # posts = db.query(models.Post).filter(models.Post.owner_id == user.id).all()
    return posts


@router.get('/{id}', response_model=schemas.PostResponseWithLikes)
# fastapi will check that the id path variable can be converted to an integer, then automatically convert it for us
def get_post(id: int, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    # since we know there is only one post with a matching id, we can use .first instead of .all
    post = db.query(models.Post, func.count(models.Like.post_id).label('likes')).join(models.Like, models.Post.id ==
                                                                                      models.Like.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} does not exist')
    # if post.owner_id != user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail='Not authorized to perform requested action')
    return post


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    # review unpacking dictionaries
    new_post = models.Post(owner_id=user.id, **post.dict())
    db.add(new_post)
    db.commit()
    # not sure how this works
    db.refresh(new_post)
    # fastapi will automatically convert dicts, lists, pydantic models, ORM models, and other objects to json
    return new_post


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    query = db.query(models.Post).filter(models.Post.id == id)
    post = query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} does not exist')
    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')
    query.delete(synchronize_session=False)
    db.commit()
    # is this redundant?
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    query = db.query(models.Post).filter(models.Post.id == id)
    post = query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} does not exist')
    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')
    query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return query.first()
