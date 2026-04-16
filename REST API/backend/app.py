from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session, select

#scores = []

class ScoreBase(SQLModel):
    name: str = Field()
    score: int = Field()

class Score(ScoreBase, table=True): 
    id: int | None = Field(default=None, primary_key=True) #Field == column

class ScoreCreate(ScoreBase):
    pass

class ScoreRead(ScoreBase):
    id: int


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    action: str
    target: str
    remaining_bricks: int


engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)


app = FastAPI()

#---#

@app.get("/score")
async def get_all_scores():
    with Session(engine) as session:
        statement = select(Score).order_by(Score.score.asc())
        results = session.exec(statement).all()
        return results

@app.get("/score/{username}")
async def get_user_scores(username: str):
    with Session(engine) as session:
        statement = select(Score).where(Score.name == username).order_by(Score.score.asc())
        results = session.exec(statement).all()
        return results

#@app.get("/score/{username}")
#async def get_user_scores(username: str) -> list[dict]:
#    filtered_scores = []
#    
#    for entry in scores:
#        if entry['name'] == username:
#            filtered_scores.append(entry)
#
#    return sorted(filtered_scores, key=lambda item: item['score'], reverse=False)

@app.post("/score")
async def post_score(score: ScoreCreate) -> ScoreRead:
    db_score = Score.model_validate(score)
    with Session(engine) as session:
        session.add(db_score)
        session.commit()
        session.refresh(db_score)
        return db_score
    #scores.append(score)
    #return scores

#---#

#events = []

@app.post("/event")
async def post_event(event: Event):
    with Session(engine) as session:
        session.add(event)
        session.commit()
        session.refresh(event)
        return {"status": "received", "data": event}

@app.get("/event")
async def get_events_from_db():
    with Session(engine) as session:
        statement = select(Event).order_by(Event.id.desc()).limit(10)
        results = session.exec(statement).all()
        return results