from fastapi import FastAPI
from .models import Base
from .database import engine

from .routers import auth, todos, admin, user


app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
