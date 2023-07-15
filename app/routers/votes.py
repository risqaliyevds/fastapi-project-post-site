from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session

from app import oauth2, schemas, models, get_database

router = APIRouter(
    tags=['Votes'],
    prefix='/votes'
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote_post(vote: schemas.Vote,
                    db: Session = Depends(get_database.get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {vote.post_id} not found!!!')

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                              models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if vote.vote_direction == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Post already voted!!!')
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "succesfuly voted"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote doesn't exist!!!")
        vote_query.delete()
        db.commit()
        return {"message": "succesfuly deleted vote"}
