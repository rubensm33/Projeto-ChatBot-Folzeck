from typing import Literal, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import update
from models import Users
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class User(BaseModel):
    name: str 
    lastname: str
    user_id: Optional[str]
    age: int
    genre: Literal["Male", "Female"]

class PatchUser(BaseModel):
    name: Optional[str] 
    lastname: Optional [str] 
    age: Optional[int] 
    genre: Optional[Literal["Male", "Female"]]






##/ -> Root to apresentation 

@app.get("/")
async def home():
    return {"message":"Folzeck Group"}


# /list-users -> List all users
@app.get("/list-users")
async def list_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


# /list-user-by-index/{index} -> List User by Index
@app.get("/list-user-by-index/{index}")
async def list_user_by_index(index: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.user_id == index).first()
    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {index} : Does not exist"
        )
    else:
        return db.query(models.Users).filter(models.Users.user_id == index).first()



# /add-user -> Add New User
@app.post("/add-user")
async def add_user(user: User, db: Session = Depends(get_db)):
    
    user_model = models.Users()
    user_model.name = user.name
    user_model.lastname = user.lastname
    user_model.age = user.age
    user_model.genre = user.genre

    db.add(user_model)
    db.commit()

    return user
    
# /upadate-user -> Update User by Index
@app.put("/put-user/{index}")
async def put_user(user: User, index: int, db: Session = Depends(get_db)):

    user_model = db.query(models.Users).filter(models.Users.user_id == index).first()
    
    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {index} : Does not exist"
        )

    user_model.name = user.name
    user_model.lastname = user.lastname
    user_model.age = user.age
    user_model.genre = user.genre

    db.add(user_model)
    db.commit()

    return user


# /upadate-partially-user -> Update User Partially by Index
@app.patch("/patch-user/{index}")
async def patch_user(index: int, patch_user: PatchUser, db: Session = Depends(get_db)):
   update_query = (update(Users)).values(patch_user.dict(exclude_unset=True)).where(Users.user_id == index)
   db.execute(update_query)
   db.commit()
   return "USUARIO ATUALIZADO" 



# /delete-user-by-index/{index} -> Delete User by Index
@app.delete("/delete-user-by-index/{index}")
async def delete_user_by_index(index: int,  db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.user_id == index).first()


    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {index} : Does not exist"
        )
    db.query(models.Users).filter(models.Users.user_id == index).delete()
    db.commit()



#/delete-all-users -> Delete all users from database

@app.delete("/delete-all-users")
async def delete_all_users(db: Session = Depends(get_db)):
    

    db.query(models.Users).delete()
    db.commit()