"""Main module for an example FastAPI project"""
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import PostCreate, PostResponse

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

posts: list[PostResponse] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": ("Python is a great language for web development,"
        " and FastAPI makes it even better."),
        "date_posted": "April 21, 2025",
    },
]


@app.get('/', include_in_schema=False, name="home")
@app.get('/posts', include_in_schema=False, name="posts")
async def home(request: Request):
    """Home Page"""
    return templates.TemplateResponse(request, "home.html", {'posts': posts, 'title': 'Home'})


@app.get('/posts/{post_id}', include_in_schema=False)
async def post_page(request: Request, post_id: int):
    """Route to return blog post by id"""
    post = next((post for post in posts if post['id'] == post_id), None)
    if post is not None:
        title = post['title'][:50]
        return templates.TemplateResponse(request, "post.html", {'post': post, 'title': title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get('/api/posts', response_model=list[PostResponse])
async def get_posts():
    """API Route to GET all Blog Posts"""
    return posts


@app.get('/api/posts/{post_id}', response_model=PostResponse)
async def get_post(post_id: int):
    """API Route to GET a Blog Post by ID"""
    post = next((post for post in posts if post['id'] == post_id), None)
    if post is not None:
        return post
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.post('/api/posts', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate):
    """API Route to POST a New Blog Post"""
    new_id = max(p['id'] for p in posts) + 1 if posts else 1
    new_post = {
        'id': new_id,
        'author': post.author,
        'title': post.title,
        'content': post.content,
        'date_posted': 'May 17, 2026'
    }
    posts.append(new_post)
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
