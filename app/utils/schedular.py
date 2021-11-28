from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_date
from models import  Schedule
import datetime
import requests
import calendar
import pytz
import os
import json
import sys

EXPERIENCE_SERVICE_URL = os.getenv('EXPERIENCE_SERVICE_URL')

def task(db: Session) -> None:
    all_schedules = db.query(Schedule).all()
   
    for schedule in all_schedules:
        print('SCHEDULE #'+schedule.id)
        print('unix', datetime.datetime.now().timestamp())
        frequency = schedule.frequency1.code.split('-',1)
        # print('DIFF', schedule.last_check.timestamp()+50 - datetime.datetime.now(tz=pytz.timezone('asia/colombo')).timestamp())
        if frequency[0] == 'daily':
            if schedule.last_check == None or schedule.last_check.timestamp() + (24*3600) < datetime.datetime.now().timestamp():
                daily_scheduler(db, schedule)
        
        if frequency[0] == 'weekly':
            if schedule.last_check == None or schedule.last_check.timestamp() + (7*24*3600) < datetime.datetime.now().timestamp():
                weekly_scheduler(db, schedule, frequency[1])

        if frequency[0] == 'monthly':
            if schedule.last_check == None or schedule.last_check.timestamp() + (28*24*3600) < datetime.datetime.now().timestamp():
                monthly_scheduler(db, schedule, frequency[1])

        


def daily_scheduler(db, schedule):
    schedule.last_check = datetime.datetime.now().isoformat()
    #run scan
    response = requests.post(EXPERIENCE_SERVICE_URL+'/experience-service/v1/bulk-scan', data=json.dumps({'reference':schedule.reference}), headers={"Content-Type":"application/json"})
    print(str(response), file=sys.stdout)
    db.add(schedule)
    db.commit() 

def weekly_scheduler(db, schedule, occurance):
    if(occurance == datetime.datetime.now().strftime('%a').lower()):
        #run scan
        response = requests.post(EXPERIENCE_SERVICE_URL+'/experience-service/v1/bulk-scan', data=json.dumps({'reference':schedule.reference}), headers={"Content-Type":"application/json"})
        schedule.last_check = datetime.datetime.now().isoformat()
        db.add(schedule)
        db.commit()

def monthly_scheduler(db, schedule, occurance):
    if(occurance == '1' and datetime.datetime.now().strftime('%-d')==1):
        response = requests.post(EXPERIENCE_SERVICE_URL+'/experience-service/v1/bulk-scan', data=json.dumps({'reference':schedule.reference}), headers={"Content-Type":"application/json"})
        schedule.last_check = datetime.datetime.now().isoformat()
        db.add(schedule)
        db.commit()

    if(occurance == '0' and datetime.datetime.now().strftime('%Y-%m-')+str(calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1])==datetime.datetime.now().strftime('%Y-%m-%d')):
        response = requests.post(EXPERIENCE_SERVICE_URL+'/experience-service/v1/bulk-scan', data=json.dumps({'reference':schedule.reference}), headers={"Content-Type":"application/json"})
        schedule.last_check = datetime.datetime.now().isoformat()
        db.add(schedule)
        db.commit()