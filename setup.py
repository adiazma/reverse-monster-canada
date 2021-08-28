from requests import Session
import monster, json, time, re
from datetime import datetime

global session

def AuthSession():
    session = Session()
    session.headers = monster.headers
    session = monster.Auth(session)
    variable = {'session_info': monster.get_session_cookies(session)}
    print(json.dumps(variable))

def StartSession():
    session = Session()
    session.headers = monster.headers
    #monster.set_session_cookies(session, json.loads(open('creds.json').read())['session_info'])
    return session

def LoopSession():
    offset = 0
    while True:
        employees = monster.SearchEmployees(session, offset=offset)['jobResults']
        for item in employees:
            print(item['jobId'])
        time.sleep(3)
        offset += len(employees)

session = StartSession()
LoopSession()
