from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import common_params, get_db, get_secret_random
from schemas import CreateSchedule
from sqlalchemy.orm import Session
from typing import Optional
from models import Frequency, Schedule
from dependencies import get_token_header
import uuid
from datetime import datetime
from exceptions import username_already_exists
from sqlalchemy import over
from sqlalchemy import engine_from_config, and_, func, literal_column, case
from sqlalchemy_filters import apply_pagination
import time
import os
import uuid
from sqlalchemy.dialects import postgresql
import base64

page_size = os.getenv('PAGE_SIZE')

router = APIRouter(
    prefix="/v1/schedules",
    tags=["SchedulerAPIs"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

@router.get("/frequencies")
def get_by_filter(db: Session = Depends(get_db)):
    freq = db.query(Frequency).all()

    response = {
        "data": freq
    }

    return response

@router.post("")
def create(details: CreateSchedule, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    id = details.id or uuid.uuid4().hex

    schedule = Schedule(
        id=id,
        start=details.start,
        terminate=details.terminate,
        frequency=details.frequency,
        reference=details.reference,
        active=details.active
    )

    #commiting data to db
    try:
        db.add(schedule)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail="Unable to create schedule")
    return {
        "id": schedule.id
    }

@router.get("/references/{id}")
def get_by_ref_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.reference == id.strip()).one()
    if schedule == None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    response = {
        "data": schedule
    }
    return response

@router.put("/references/{id}")
def update_by_ref_id(id: str, details: CreateSchedule, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
        
    schedule = db.query(Schedule).filter(Schedule.reference == id).one()

    if details.active == True:
        active = 1
    else:
        active = 0

    schedule.id = id
    schedule.start=details.start
    schedule.terminate=details.terminate
    schedule.frequency=details.frequency
    schedule.active=active

    try:
        db.add(schedule)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail="failed to update")
    return {
        "success": True
    }

# @router.delete("/{id}")
# def delete_by_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
#     credentail = db.query(Secret).get(id.strip())
#     db.delete(credentail)
#     db.commit()
#     return Response(status_code=204)

