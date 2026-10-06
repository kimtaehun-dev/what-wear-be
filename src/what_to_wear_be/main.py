from fastapi import FastAPI
from .database import SessionLocal
from .models import TestTable
from sqlalchemy import select

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def get_test():
    with SessionLocal() as session:
        statement = select(TestTable)
        result = session.scalars(statement).all()

        return [
            {
                "id": row.id,
                "name": row.name,
                "age": row.age,
            }
            for row in result
        ]