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

def LoopSession(session, label='python'):
    offset = 0
    while True:
        try:
            employees = monster.SearchEmployees(session, offset=offset, label=label)['jobResults']
        except:
            break
        if len(employees) == 0:
            break
        for item in employees:
            if item['jobId'] in repeat:
                continue
            repeat.append(item['jobId'])
            if item['status'] not in ('ACTIVE'):
                continue
            if item['apply']['applyType'] not in ('ONSITE'):
                continue
            print(item['jobId'], item['formattedDate'], item['jobPosting']['title'])
            try:
                monster.ApplyJob(session, item['jobId'])
                print('-----> Applied!')
            except:
                print('-----> Error!')
                
            time.sleep(1)
        
        offset += len(employees)
        time.sleep(3)

session, repeat = AuthSession(), []
while True:
    LoopSession(session, 'startup')
    LoopSession(session, 'data')
    LoopSession(session, 'data engineer')
    LoopSession(session, 'sql')
    LoopSession(session, 'python')
    LoopSession(session, 'etl')
    LoopSession(session, 'web scraping')
    LoopSession(session, 'data mining')
    
