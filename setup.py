from requests import Session
import monster, json, time, os
from datetime import datetime

global session

def AuthSession():
    session = Session()
    session.headers = monster.headers
    creds = json.loads(open(f'{os.getcwd()}/creds.json', 'rb').read())
    session = monster.Auth(session, creds)
    

def StartSession():
    session = Session()
    session.headers = monster.headers
    return session

def LoopSession():
    offset = 0
    while True:
        employees = monster.SearchEmployees(session, offset=offset)['jobResults']
        for item in employees:
            print(item['jobId'], item['formattedDate'], item['apply']['applyType'], item['status'], item['jobPosting']['title'])
        time.sleep(3)
        offset += len(employees)

AuthSession()
