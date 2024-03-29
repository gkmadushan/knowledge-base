from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import common_params, get_db, get_secret_random
from schemas import CreateReport
from sqlalchemy.orm import Session
from typing import Optional
from models import LessonLearntReport, Reference
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
import json
from sqlalchemy.dialects import postgresql
import base64

page_size = os.getenv('PAGE_SIZE')

router = APIRouter(
    prefix="/v1/reports",
    tags=["KnowledgeBaseAPI"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

@router.post("")
def create(details: CreateReport, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    id = details.id or uuid.uuid4().hex

    report = LessonLearntReport(
        id=id,
        description=details.description,
        submitted_at=datetime.now(),
        issue_id=details.issue_id,
        title=details.title
    )

    try:
        refs = json.loads(base64.b64decode(details.ref))
        for ref in refs:
            reference = Reference(
                id=uuid.uuid4().hex,
                reference=ref['ref'],
                type=ref['type'],
                report=id
            )
            db.add(reference)
    except:
        pass

    #commiting data to db
    try:
        db.add(report)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail="Unable to create schedule")
    return {
        "id": report.id
    }

@router.get("")
def get_by_filter(page: Optional[str] = 1, limit: Optional[int] = page_size, commons: dict = Depends(common_params), db: Session = Depends(get_db), id: Optional[str] = None, ref: Optional[str] = None, issue: Optional[str] = None):
    filters = []

    if(id):
        filters.append(LessonLearntReport.id == id)

    if(ref):
        filters.append(Reference.reference.ilike('%'+ref+'%'))
    
    if(issue):
        filters.append(LessonLearntReport.issue_id == issue)

    query = db.query(
        over(func.row_number(), order_by=LessonLearntReport.submitted_at).label('index'),
        LessonLearntReport.id,
        LessonLearntReport.description,
        LessonLearntReport.submitted_at,
        LessonLearntReport.issue_id,
        LessonLearntReport.title
    )

    query, pagination = apply_pagination(query.where(and_(*filters)).join(Reference.lesson_learnt_report).group_by(LessonLearntReport.id, LessonLearntReport.description, LessonLearntReport.submitted_at, LessonLearntReport.issue_id).order_by(LessonLearntReport.submitted_at.asc()), page_number = int(page), page_size = int(limit))

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

@router.get("/{id}")
def get_by_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    report = db.query(LessonLearntReport).get(id.strip())
    
    if report == None:
        raise HTTPException(status_code=404, detail="Report not found")
    response = {
        "data": report
    } 
    return response