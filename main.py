"""Main module for an example FastAPI project"""
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/media', StaticFiles(directory='media'), name='media')

templates = Jinja2Templates(directory='templates')


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    """Home route"""
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.get('/posts/{post_id}', include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    """Route to return blog post by id"""
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """Route to get all Blog Posts for a given user"""
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.get('/api/users/{user_id}', response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """API Route to GET a User by ID"""
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


@app.post('/api/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """API Route to POST a User"""
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Username already exists')
    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Email is already in use')
    new_user = models.User(
        username=user.username,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """API Route to get Blog Posts for a given User"""
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


@app.get('/api/posts', response_model=list[PostResponse])
async def get_posts(db: Annotated[Session, Depends(get_db)]):
    """API Route to GET all Blog Posts"""
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts


@app.get('/api/posts/{post_id}', response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    """API Route to GET a Blog Post by ID"""
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.post('/api/posts', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    """API Route to POST a New Blog Post"""
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    """Method for handling general HTTP Exceptions"""
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    """Method to handle validation errors"""
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
