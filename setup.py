from requests import Session
import monster, json, time, os
from datetime import datetime

global session

def AuthSession():
    session = Session()
    session.headers = monster.headers
    creds = json.loads(open(f'{os.getcwd()}/creds.json', 'rb').read())
    session = monster.Auth(session, creds)
    return session

def LoopSession(session):
    offset = 0
    while True:
        employees = monster.SearchEmployees(session, offset=offset)['jobResults']
        for item in employees:
            print(item['apply'])
            print(item['jobId'], item['formattedDate'], item['jobPosting']['title'])
            if item['status'] not in ('ACTIVE'):
                continue
            if item['apply']['applyType'] not in ('ONSITE'):
                continue
            monster.ApplyJob(session, item['jobId'])
            print('-----> Applied!')
            time.sleep(1)
        
        offset += len(employees)
        time.sleep(3)

session = AuthSession()
LoopSession(session)
