from collective.beaker.interfaces import ISession
from pymongo import MongoClient
from bson.objectid import ObjectId
from App.config import getConfiguration
config = getConfiguration()
configuration = config.product_config.get('mongodb', dict())
mongoserver = configuration.get('mongoserver')
mongoport = int(configuration.get('mongoport'))

def getSessionData(request):
    """
    Liest das SessionCookie
    """
    session = ISession(request)
    mongo_objid = session.get('key', '')
    client = MongoClient(mongoserver, mongoport)
    db = client.hh_database
    collection = db.hh_collection
    if mongo_objid:
        print 'lesen: ',mongo_objid
        data = collection.find_one({"_id":mongo_objid})
    else:
        data = {'hhlpan':False,
                'taetigkeit':{},
                'chemiesuche':{},
                'cbsuche':{},
                'mechaniksuche':{},
                'schutzhandschuhe':[],
                'hautschutz':[],
                'hautreinigung':[],
                'hautpflege':[],
                'desinfektion':[],
                'hautschutzplan':{}}
    return data

def setSessionData(request, data):
    """
    Schreibt das Cookie in die Session
    """
    session = ISession(request)
    mongo_objid = session.get('key', '')
    client = MongoClient(mongoserver, mongoport)
    db = client.hh_database
    collection = db.hh_collection
    if mongo_objid:
        insert = collection.replace_one({'_id':mongo_objid}, data, upsert=True)
        session.save()
    else:
        insert = collection.insert_one(data).inserted_id
        session['key'] = insert
        session.save()
    return insert

def delSessionData(request):
    """
    Loescht das Cookie
    """
    data = {'hhlpan':False,
            'taetigkeit':{},
            'chemiesuche':{},
            'mechaniksuche':{},
            'schutzhandschuhe':[],
            'hautschutz':[],
            'hautreinigung':[],
            'hautpflege':[],
            'desinfektion':[],
            'hautschutzplan':{}}
    insert = setSessionData(request, data)
    session = ISession(request)
    session.delete()
