from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import posts, users, auth, votes

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#origins = ['https://www.google.com']
app.add_middleware(CORSMiddleware,
                   allow_origins = ["*"], #origins,
                   allow_credentials = True,
                   allow_methods = ["*"],
                   allow_headers = ["*"])

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(votes.router)

@app.get("/")
def root():
    return {"message": "Hello world!!!"}
