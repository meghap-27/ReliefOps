from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from priority import compute_priority
from matching import find_best_match

app = FastAPI()
connected_clients: list[WebSocket] = []
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/tasks")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    t = models.Task(**task.dict())
    t.priority_score = compute_priority(t)
    db.add(t); db.commit(); db.refresh(t)
    trigger_reassignment(db)          # re-evaluate all on every new task
    return t

@app.post("/volunteers")
def register_volunteer(vol: schemas.VolunteerCreate, db: Session = Depends(get_db)):
    v = models.Volunteer(**vol.dict())
    db.add(v); db.commit(); db.refresh(v)
    return v

@app.get("/assignments")
def get_assignments(db: Session = Depends(get_db)):
    tasks = db.query(models.Task)\
              .filter(models.Task.status != models.TaskStatus.done)\
              .order_by(models.Task.priority_score.desc())\
              .all()
    return tasks

@app.websocket("/live")
async def live_updates(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True: await ws.receive_text()
    except:
        connected_clients.remove(ws)

def trigger_reassignment(db: Session):
    pending = db.query(models.Task)\
                .filter(models.Task.status == models.TaskStatus.pending)\
                .order_by(models.Task.priority_score.desc())\
                .all()
    volunteers = db.query(models.Volunteer).all()
    for task in pending:
        best = find_best_match(task, volunteers)
        if best:
            task.assigned_to = best.id
            task.status      = models.TaskStatus.assigned
            best.available   = False
    db.commit()
@app.get("/volunteers")
def get_volunteers(db: Session = Depends(get_db)):
    return db.query(models.Volunteer).all()
