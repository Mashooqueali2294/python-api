from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, create_engine, Session, SQLModel, select
from datetime import datetime

class Clients(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    email: str
    phone_number: str
    company_name: str
    status: str
    create_at: datetime | None= Field(default_factory=datetime.utcnow, index=True)

postgres_url = "postgresql://postgres:Mashooque2294@localhost/postgres"
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

@app.post("/Clients")
def create_client(client: Clients, session: SessionDep)->Clients:
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@app.get("/Clients")
def ge_t_clients(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
)-> list[Clients]:
    offer_client = session.exec(select(Clients).offset(offset).limit(limit)).all()
    return offer_client

@app.get("/Clients/{client_id}")
def id_client(client_id: Clients, session: SessionDep):
    offer = session.get(Clients, client_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Clients not Found in this Company")
    return offer

@app.delete("/Clients/{client_id}")
def delete_client_from_company(client_id: Clients, session: SessionDep):
    offer = session.get(Clients, client_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Clients not Found in this Company")
    session.delete(offer)
    session.commit()
    return {"message": f"Client {client_id} deleted successfully"}
