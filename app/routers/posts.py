from fastapi import Depends, status, HTTPException, Response, APIRouter
from app.get_database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.Post])
async def get_posts(db: Session = Depends(get_db),
                    current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    return posts


@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[schemas.PostOut])
def get_all_posts(db: Session = Depends(get_db),
                  limit: int = 10,
                  skip: int = 0,
                  search: Optional[str] = ""):
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .outerjoin(models.Vote, models.Post.id==models.Vote.post_id) \
        .group_by(models.Post.id) \
        .filter(models.Post.title.contains(search)) \
        .limit(limit) \
        .offset(skip) \
        .all()

    serialized_results = []
    for post, vote_count in posts:
        serialized_post = schemas.PostOut(
            post=schemas.Post(**post.__dict__),
            votes=vote_count,
            owner=schemas.UserOut(**post.owner.__dict__)  # Assuming the owner field exists in the Post model
        )
        serialized_results.append(serialized_post)

    return serialized_results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return schemas.PostOut(post=new_post, votes=0)


@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int,
                   db: Session = Depends(get_db)):
    post, vote_count = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id) \
        .filter(models.Post.id == id) \
        .first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id -> {id} not found!"
        )

    return schemas.PostOut(post=post, votes=vote_count)


@router.delete("/{id}")
async def delete_post(id: int,
                      db: Session = Depends(get_db),
                      current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id -> {id} doesn't exist!")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Post with id -> {id} not yours!")

    db.delete(post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostOut)
async def update_post(id: int,
                      post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    existing_post = db.query(models.Post).filter(models.Post.id == id).first()

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id -> {id} not found!")

    if existing_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Post with id -> {id} not yours!")

    existing_post.title = post.title
    existing_post.content = post.content
    existing_post.published = post.published
    db.commit()
    db.refresh(existing_post)

    return schemas.PostOut(post=existing_post, votes=0)