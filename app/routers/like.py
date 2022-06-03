from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/like',
    tags=['Like']
)

# should we combine the like and unlike path operations?
@router.post('/{post_id}', status_code=status.HTTP_201_CREATED)
def like(post_id: int, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {post_id} does not exist')
    like = db.query(models.Like).filter(models.Like.post_id ==
                                        post_id, models.Like.user_id == user.id).first()
    if like:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'user {user.id} has already liked post {post_id}')
    new_like = models.Like(post_id=post_id, user_id=user.id)
    db.add(new_like)
    db.commit()
    return {'message': 'successfully liked post'}


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def unlike(post_id: int, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {post_id} does not exist')
    query = db.query(models.Like).filter(models.Like.post_id ==
                                         post_id, models.Like.user_id == user.id)
    like = query.first()
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user {user.id} has not liked post {post_id}')
    query.delete(synchronize_session=False)
    db.commit()
    # is this redundant?
    return Response(status_code=status.HTTP_204_NO_CONTENT)
