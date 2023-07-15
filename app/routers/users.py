from fastapi import Depends, status, HTTPException, APIRouter
from app.get_database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, utils

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user_info: schemas.UserCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.email == user_info.email)
    user = user_query.first()

    if user:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail=f"User with email -> {user_info.email} alredy exists")

    user_info.password = utils.hashing(user_info.password)

    new_user = models.User(**user_info.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not found!")

    return user
