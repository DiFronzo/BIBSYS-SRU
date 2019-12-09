# -*- coding: utf-8  -*-
import requests
import xmltodict
import json


SRU_PATHS = {
    'bibsys': 'https://authority.bibsys.no/authority/rest/sru?',
    'bibauth': 'https://authority.bibsys.no/authority/rest/authorities/v2/',
}

script_version = '0.1.3'
api_version = '1.2'

# main 
class SRU():
    def __init__(self, r, zone="", sru_path="", printOut=""):
        self.zone = zone
        self.r = r
        self.xml = r.text or ""
        self.dict = xmltodict.parse(self.xml, dict_constructor=dict)
        self.list = []
        self.printOut = printOut
        print(self.printOut)
        # get number of records, check for errors
        try:
            self.numberOfRecords = int(self.dict['srw:searchRetrieveResponse']['srw:numberOfRecords'])
            self.ok = True
            self.errors = None
        except Exception as e:
            self.numberOfRecords = 0
            self.ok = False
            self.errors = self.dict['srw:searchRetrieveResponse']['srw:diagnostics']['srw:diag:diagnostic']['srw:diag:message']
            print(f"{e}\n{self.xml}")

        if self.numberOfRecords > 0:
            for val in self.dict['srw:searchRetrieveResponse']['srw:records']['srw:record']:
                ident = checkPerson(val['srw:recordIdentifier'])
                if ident != -1:
                    self.list.append(get_authorities(ident))
                
        if self.list and self.printOut == "yes":
            for ent in self.list:
                printText(ent)
            
def search(query=""):
    r = requests.get(query)
    return r

def make_url(zone="", query="", operation="searchRetrieve", 
                   recordSchema="marcxchange", maximumRecords="15", startRecord="1", packing="xml"):
    sru_path = SRU_PATHS[zone]
    url = f"{sru_path}?version={api_version}&operation={operation}&recordSchema={recordSchema}&maximumRecords={maximumRecords}&startRecord={startRecord}&query={query}&recordPacking={packing}"
    return url

def parse(r, zone="", printOut=""):
    sru_object = SRU(r, zone, printOut)
    return sru_object

def checkPerson(auth, zone='bibauth', packing='json'):
    sru_path = SRU_PATHS[zone]
    url = f"{sru_path}{auth}?format=json"
    r2 = requests.get(url)
    r2.encoding = 'UTF-8'
    file = r2.json()
    if file['authorityType'] == 'PERSON':
        return file
    else:
        return -1

def get_authorities(file2):
    file = file2
    values = {u'status': file['status'], u'id': file['systemControlNumber'], u'100': {}, u'400': {}, u'43': {}, u'680': {}, u'isni': '', u'viaf': '', u'gender': ''}
    
    if file['deleted'] == False:
        
        for marc in file['marcdata']:
            if marc['tag'] == str(100):
                for sub in marc['subfields']:
                    values['100'].setdefault(sub['subcode'],[]).append(sub['value'])
                    
            if marc['tag'] == str(400):
                for sub in marc['subfields']:
                    values['400'].setdefault(sub['subcode'],[]).append(sub['value'])

            if marc['tag'] == '043':
                for sub in marc['subfields']:
                    values['43'].setdefault(sub['subcode'],[]).append(sub['value'])
                    
            if marc['tag'] == str(680):
                for sub in marc['subfields']:
                    values['680'].setdefault(sub['subcode'],[]).append(sub['value'])
                    
            if marc['tag'] == str(375):
                for sub in marc['subfields']:
                    values['gender'] = ('male' if sub['value'] == 'm' else 'female')
                    
        for ident in file['identifiersMap']:
            if ident == 'isni':
                values['isni'] = file['identifiersMap']['isni']
            if ident == 'viaf':
                values['viaf'] = file['identifiersMap']['viaf']
    else:
        return ""
    
    return(values)

def printText(ent):
    if ent[u'100'][u'a'] and ent[u'100'][u'd']:
        print("Foretrukket navneform: {}, {}".format(ent["100"]['a'],ent["100"]['d']))
    else:
        print("Foretrukket navneform: {}".format(ent["100"]['a']))
    print("Type: {}".format('Person'))
    if ent[u'400'] and ent[u'400'][u'a']:
        print("Navnevarianter: {}".format(ent['400']['a']))
    if ent['gender']:
        print("Kjønn: {}".format(ent['gender']))
    if ent['43'] and ent['43']['c']:
        print("Land/sted: {}".format(ent['43']['c']))
    if ent['680'] and ent['680']['a']: 
        print("Note: {}".format(ent['680']['a']))
    if ent['isni'] or ent['viaf']:
        print('Identifikatorer')
    if ent['isni']:
        print("ISNI: {}".format(ent['isni']))
    if ent['viaf']:
        print("VIAF: {}".format(ent['viaf']))
    print("Lokal autoritets-ID: {}".format(ent['id']))
    print("Kvalitetsnivå: {}".format(ent['status']))
    print('________________________')
