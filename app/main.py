from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os
from dotenv import load_dotenv
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()

while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT"),
            cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
     
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)



my_posts = [{"title": "title of post 1", "content": "content of post 1 ", "id": 1}, {"title": "favourite foods", "content": "I like pizza ", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, j in enumerate(my_posts):
        if j['id'] == id:
            return i

@app.get("/")
async def root():
    return "root"

@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()

    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title,content, published) VALUES(%s ,%s ,%s ) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return {"post_details": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id)


    if deleted_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post with id : {id} does not exist")

    deleted_post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id:int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """ , (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return {"message": post_query.first()}