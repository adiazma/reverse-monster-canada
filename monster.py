from requests import Session, Response, Request
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import json, os, requests, mysql.connector, math
import base64

BASE_URL = 'www.linkedin.com'

HOST = '192.168.1.105'

DATABASE = 'productos'

USER = 'admin'

PASSWORD = 'admin'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'es-419,es;q=0.9',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'upgrade-insecure-requests': '1'
}

# Functions
def set_session_cookies(_session, cookies):
    for cookie in cookies:
        if 'httpOnly' in cookie:
            cookie['rest'] = {'httpOnly': cookie.pop('httpOnly')}
        if 'expiry' in cookie:
            cookie['expires'] = cookie.pop('expiry')
        if 'sameSite' in cookie:
            cookie.pop('sameSite')
        _session.cookies.set(**cookie)

def get_session_cookies(session, filters=[]):
    cookies = []
    if session:
        for cookie in session.cookies:
            if filters and cookie.name not in filters:
                continue
            cookie_dict = {'name': cookie.name, 'value': cookie.value}
            if cookie.domain:
                cookie_dict['domain'] = cookie.domain
            cookies.append(cookie_dict)
    return cookies

# Monster
def SearchEmployees(_session, offset=10, label='python'):
    url = f"https://services.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/en-ca"
    request = Request('POST', url=url, headers=headers, data=str.encode(json.dumps({
        'jobQuery': {
            'locations': [{'address': '', 'country': 'ca', 'radius': {'unit': 'km', 'value': '20'}}], 
            'excludeJobs': [], 
            'companyDisplayNames': [], 
            'query': label,
        }, 
        'offset': offset, 
        'pageSize': 10, 
        'searchId': '',
        'fingerprintId': '', 
        'includeJobs': [],
        'jobAdsRequest': {
            'position': list(range(1, 11)), 
            'placement': {'component': 'JSR_LIST_VIEW', 'appName': 'monster'}
        }
    })))
    req = _session.prepare_request(request)
    response = _session.send(req)

    return json.loads(response.content)

# LinkedIn
def Auth(_session, creds={}):
    url = f'https://www.monster.com/profile/detail'
    request = Request('GET', url=url, headers=headers)
    req = _session.prepare_request(request)
    response = _session.send(req)
    item = json.loads(base64.b64decode(response.text.split('window.atob("')[1].split('"')[0]))

    url = f"https://identity.monster.com/usernamepassword/login"
    request = Request('POST', url=url, data=str.encode(json.dumps({
        'audience': 'profiles-profile-app-service',
        'client_id': item['clientID'],
        'connection': 'Username-Password-Authentication',
        'password': creds['password'],
        'redirect_uri': 'https://www.monster.com/profile/auth/callback',
        'response_type': 'code',
        'scope': item['internalOptions']['scope'],
        'state':item['internalOptions']['state'],
        'tenant': 'monster-candidate-prod',
        'username': creds['username'],
        '_csrf': item['internalOptions']['_csrf'],
        '_intstate': item['internalOptions']['_intstate'],
    })), headers={
         **headers,
         'content-type': 'application/json',
         'origin': 'https://identity.monster.com',
         'referer': response.url
    })
    req = _session.prepare_request(request)
    response = _session.send(req)

    print(response.text)

    return _session

# SQL
def DiccionarioSQL(Select):
    cnxn = mysql.connector.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD, charset='latin1', auth_plugin='mysql_native_password')
    cursor = cnxn.cursor(buffered=True)
    cursor.execute(Select)
    cnxn.commit()
    Header, Respuesta = [column[0] for column in cursor.description], []
    for idx, Rows in enumerate(list(cursor.fetchall())) or []:
        Resultado = [x for x in Rows]
        Lista = {y: Resultado[idy] for idy, y in enumerate(Header)}
        Respuesta.append(Lista)
    cnxn.close()
    return Respuesta

def DiccionarioStore(store, values):
    cnxn = mysql.connector.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD, charset='latin1', auth_plugin='mysql_native_password')
    cursor = cnxn.cursor(buffered=True)
    cursor.callproc(str(store), values)
    for result in cursor.stored_results():
        description = result.description
        fetch = result.fetchall()
    Header, Respuesta = [column[0] for column in description], []
    for idx, Rows in enumerate(list(fetch)) or []:
        Resultado = [x for x in Rows]
        Lista = {y: Resultado[idy] for idy, y in enumerate(Header)}
        Respuesta.append(Lista)
    cnxn.close()
    return Respuesta

def Execute(Update, Multi=False):
    cnxn = mysql.connector.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD, auth_plugin='mysql_native_password')
    cursor = cnxn.cursor()
    cursor.execute(Update)
    cnxn.commit()
    cursor.close()
    cnxn.close()

import re
def InsertarTabla(Todo, Tabla = ''):
    if len(Todo)>0:
        Corte = 500
        SubA = DiccionarioSQL(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS WHERE TABLE_NAME = '{Tabla}'")
        SubA = [a for a in SubA if a['COLUMN_NAME'] in Todo[0].keys()]
        def NonLatin(text): 
            return deEmojify(text.replace("'", '').replace("’", '').replace("’", '').replace("“", '').replace("”", ''))
        Residuo, Paso, Pasos = len(Todo)%Corte, 0, math.floor(len(Todo)/Corte)
        while True:
            Siguiente = Paso*Corte + (Corte if Paso!=Pasos else Residuo)
            Grupo = Todo[Paso*Corte:Siguiente]; Paso+=1;
            if Grupo == []: break;
            def Formato(a, b):
                SubB = [c for c in SubA if c['COLUMN_NAME'] == b['COLUMN_NAME']]
                b = a[b['COLUMN_NAME']] 
                if b == None or b == 'None': return 'NULL'
                if len(SubB)==0: return "'" + str(b).replace("'", "") + "'" if str(b)!='' else 'NULL'
                if SubB[0]['DATA_TYPE'] not in ('varchar','char','datetime'): return "'" + str(b).replace("'", "").replace("\\", "") + "'" if str(b)!='' else 'NULL'
                if SubB[0]['DATA_TYPE'] in ('datetime'): return "'" + str(b).replace("'", "").replace("\\", "") + "'" if str(b)!='' and str(b)!='0000-00-00 00:00:00' else 'NULL'
                return "'" + NonLatin(str(str(b)[:int(SubB[0]['CHARACTER_MAXIMUM_LENGTH'])]).replace('"', "").replace("'", "").replace("\\", "")) + "'" if str(b)!='' else 'NULL'
            Execute("INSERT INTO {0}({1}) VALUES {2};".format(Tabla, ",".join([str(a['COLUMN_NAME']) for a in SubA]), ", ".join(["({0})".format(" ,".join([Formato(a, b) for b in SubA])) for a in Grupo])))
            if Paso == Pasos+1: break
    else: pass
