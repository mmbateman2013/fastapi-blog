"""Main module for an example FastAPI project"""
from fastapi import FastAPI


app = FastAPI()


@app.get('/')
async def root():
    """Main route of the API"""
    return {'message': 'Hello, World'}
