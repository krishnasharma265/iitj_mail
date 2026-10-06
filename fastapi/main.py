from fastapi import FastAPI
from common.routes import auth



app=FastAPI()

app.include_router(auth.router)
