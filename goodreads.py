import requests
import json
import csv
from pprint import pprint
from xmljson import badgerfish as bf
from collections import OrderedDict
from lxml.html import Element, tostring, fromstring
import time

#PROD 
ws_server = "https://www.lakeshores.lib.wi.us/symws"
#TEST
#ws_server = "http://172.20.0.35:8080/symws"

def parse_report_file(report_input_file):
    if report_input_file[:1] != '<':
        return 'JSON'
    return 'XML'

def GetToken():
    authData = {'login':'KPL-ADTECH', 'password':'TECH'}
    authHeadres = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'sd-originating-app-id': 'cs',
                   'x-sirs-clientID': 'BCCAT'}
    tempTok = requests.post(ws_server + '/v1/user/staff/login', headers=authHeadres, data=json.dumps(authData))
    tempTok = json.loads(tempTok.text)
    genericHeader = {'Accept': 'application/json',
                     'Content-Type': 'application/json',
                     'sd-originating-app-id': 'cs',
                     'x-sirs-clientID': 'BCCAT',
                     'x-sirs-sessionToken': tempTok['sessionToken'],
                     'SD-Working-LibraryID': 'KPL-AD'}
    return {"TOKEN":tempTok['sessionToken'], "HEADER": genericHeader}

def CallAPI(method, url, payload=None, custheader=None):
    result = ''
    if custheader == None:
        TOKEN = GetToken()
        custheader = TOKEN["HEADER"]

    if url[:4] == '/v1/':
        url = ws_server + url

    if method == "POST":
        if payload == None: 
            r = requests.post(url, headers=custheader)
        else:
            r = requests.post(url, headers=custheader, data=json.dumps(payload))
    elif method == "PUT":
        if payload == None: 
            r = requests.put(url, headers=custheader)
        else:
            r = requests.put(url, headers=custheader, data=json.dumps(payload))
    elif method == "DEL":
        if payload == None: 
            r = requests.delete(url, headers=custheader)
        else:
            r = requests.delete(url, headers=custheader, data=json.dumps(payload))
    else:
        if payload == None: 
            r = requests.get(url, headers=custheader)
        else:
            r = requests.get(url, headers=custheader, params=payload)

    if r.status_code != 200:
        if r.status_code == 500:
            print(r.text)
        elif r.status_code == 404 and parse_report_file(r.text) == 'XML':
            print(r.status_code)
            print(r.url)
        else:
            print(r.status_code)
            print(r.url)
            print(r.text)
            if parse_report_file(r.text) == 'JSON':
                result = json.loads(r.text)
                if 'Could not find a(n) /catalog/bib record with the key' in result['messageList'][0]['message']:
                    print('missing record')
            else:
                print('waiting')
                time.sleep(60)
                hTOKEN = GetToken()
                CallAPI(method, url, payload, hTOKEN["HEADER"])

    if  parse_report_file(r.text) == 'JSON':
        result = json.loads(r.text)
    else:
        result = bf.data(fromstring(r.text.encode('utf8')))

    return result

#gathers information from Goodreads
#returns a dict with information about a book
def get_goodreads_info(ISBN, title):

    book = dict()

    if (ISBN != ''):
        goodReads = CallAPI('GET', 'https://www.goodreads.com/book/isbn/' + ISBN, {'format':'xml', 'key':'jU7yMys5GPXzCa92d7Q'})
        book['ISBN'] = ISBN
    elif (title != ''):
        book['title'] = title
        title.replace(' ', '%2B')
        goodReads = CallAPI('GET', 'https://www.goodreads.com/book/title?id=' + title, {'format':'xml', 'key':'jU7yMys5GPXzCa92d7Q'})
    else:
        print('Error: no title or ISBN provided for Goodreads')
        return book

    time.sleep(1)
    if 'goodreadsresponse' in goodReads:
        if 'error' not in goodReads and 'shelf' in goodReads['goodreadsresponse']['book']['popular_shelves']:
            if 'ISBN' not in book:
                book['ISBN'] = goodReads['goodreadsresponse']['book']['isbn']
            if 'title' not in book:
                book['title'] = goodReads['goodreadsresponse']['book']['title']

            book['id'] = goodReads['goodreadsresponse']['book']['id']['$']
            book['description'] = goodReads['goodreadsresponse']['book']['description']['br']
            book['pub_year'] = goodReads['goodreadsresponse']['book']['publication_year']['$']
            book['num_pages'] = goodReads['goodreadsresponse']['book']['num_pages']
            book['series_position'] = goodReads['goodreadsresponse']['book']['series_works']['series_work'][0]['user_position']['$']
    
    return book

#------------------------end-of-function-definitions----------------------------------------------------------

#for testing purposes; this isbn is for The Fellowship of the Ring
book = get_goodreads_info('9780618346271', '')
pprint(book)