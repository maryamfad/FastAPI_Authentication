from fastapi import FastAPI
import models
from database import engine, Base

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

print(Base.metadata.tables)