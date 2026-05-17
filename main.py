"""Main module for an example FastAPI project"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

posts: list[dict] = [
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


@app.get('/api/posts')
async def get_posts():
    """Route to return blog posts"""
    return posts


@app.get('/api/posts/{post_id}')
async def get_post(post_id: int):
    """Route to return blog post by id"""
    post = next((post for post in posts if post['id'] == post_id), None)
    if post is not None:
        return post
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
