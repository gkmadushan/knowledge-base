from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import common_params, get_db, get_secret_random
from schemas import CreateSchedule
from sqlalchemy.orm import Session
from typing import Optional
from models import t_lesson_learnt_report
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
    prefix="/v1/lessons-learnt",
    tags=["KnowledgeBaseAPI"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

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

@router.get("")
def get_by_filter(page: Optional[str] = 1, limit: Optional[int] = page_size, commons: dict = Depends(common_params), db: Session = Depends(get_db), id: Optional[str] = None, title: Optional[str] = None, resource: Optional[str] = None, issue_status: Optional[str] = None, issue_id: Optional[str] = None, script_available: Optional[str] = None, false_positive: Optional[str] = None, detected_at_from: Optional[str] = None, detected_at_to: Optional[str] = None, resolved_at_from: Optional[str] = None, resolved_at_to: Optional[str] = None):
    filters = []

    if(title):
        filters.append(Issue.title.ilike(title+'%'))

    if(resource):
        filters.append(Issue.resource_id == resource)

    if(issue_status):
        filters.append(Issue.issue_status_id == issue_status)

    if(issue_id):
        filters.append(Issue.issue_id == issue_id)

    if(script_available == '1'):
        filters.append(Issue.remediation_script != None)
    
    if(script_available == '0'):
        filters.append(Issue.remediation_script == None)

    if(detected_at_from):
        filters.append(Issue.detected_at >= detected_at_from)

    if(detected_at_to):
        filters.append(Issue.detected_at <= detected_at_to)

    if(resolved_at_from):
        filters.append(Issue.resolved_at >= resolved_at_from)
    
    if(resolved_at_to):
        filters.append(Issue.resolved_at <= resolved_at_to)

    if(false_positive == '1'):
        filters.append(Issue.false_positive == 1)
    
    if(false_positive == '0'):
        filters.append(Issue.false_positive == 0)


    query = db.query(
        over(func.row_number(), order_by=Issue.detected_at).label('index'),
        Issue.id,
        Issue.title,
        Issue.score,
        Issue.issue_id,
        Issue.detected_at,
        Issue.resolved_at,
        Issue.false_positive,
        IssueStatus.name.label('issue_status')
    )

    query, pagination = apply_pagination(query.where(and_(*filters)).join(Issue.issue_status).order_by(Issue.detected_at.asc()), page_number = int(page), page_size = int(limit))

    response = {
        "data": query.all(),
        "meta":{
            "total_records": pagination.total_results,
            "limit": pagination.page_size,
            "num_pages": pagination.num_pages,
            "current_page": pagination.page_number
        }
    }

    return response