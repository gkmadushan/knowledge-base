from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routers import scheduler
from fastapi.security import OAuth2PasswordBearer
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
from dependencies import get_db, get_db_config
from utils.schedular import task
import sys


app = FastAPI(debug=True)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

#middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#user routes
app.include_router(scheduler.router)

#schedule tasks
database_uri = get_db_config()
sessionmaker = FastAPISessionMaker(database_uri)
@app.on_event("startup")
@repeat_every(seconds=int(10))  # 1 minute
async def schedule_task() -> None:
    try:   
        with sessionmaker.context_session() as db:
            task(db=db)
    except:
        f = open('./error.log', 'a')
        f.write(str(sys.exc_info())+'\n')
        f.close()


