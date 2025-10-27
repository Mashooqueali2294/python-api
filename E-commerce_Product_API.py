from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, Session, select, create_engine
from datetime import datetime
from pydantic import HttpUrl

class Products(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    stock: int
    category: str
    image_url: str | None = Field(default="https://shorturl.at/JligH")
    created_at: datetime | None = Field(default_factory=datetime.utcnow)

postgres_url = "postgresql://postgres:pasword123@localhost/postgres"
engine = create_engine(postgres_url, echo=True)

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_table()

@app.post("/Products")
def create_post(products: Products, session: SessionDep)->Products:
    session.add(products)
    session.commit()
    session.refresh(products)
    return products

@app.get("/Products")
def read_product(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
)-> list[Products]:
    product = session.exec(select(Products).offset(offset).limit(limit)).all()
    return product

@app.get("/Products/{product_id}")
def get_prod(product_id: int, session: SessionDep):
    prod = session.get(Products, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not Found")
    return prod

@app.delete("/Products/{product_id}")
def delete_prod(product_id: int, session: SessionDep):
    prod = session.get(Products, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not Found")
    session.delete(prod)
    session.commit()
    return {"Message": f"products Deleted {product_id} Successfully"}
