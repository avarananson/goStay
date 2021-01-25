from pymongo import MongoClient
from pymongo import ASCENDING , DESCENDING
import logging
import psutil
logging.basicConfig(filename='{}.log'.format("flasked/logerdb"), level=logging.INFO)
gostay = 'gostay'    #name of the database
db  = None   # creating a global db  varable ,,,, in flask app use app context instead

#initate database connection
def initiatedb():
    global db
    if db is None:
        db = MongoClient('localhost', 27017)[gostay]
        return "Status of db initiation is {}".format(db is not None )
    else:
        return "Already present.."

def createcollection(name):

    db.create_collection(name) 
    logging.info("Initial ram free is {} MB".format(psutil.virtual_memory().available/1024/1024))

def getcollnames():
    filter = {"name": {"$regex": r"^(?!system\.)"}}
    return db.list_collection_names(filter=filter)

def custom_insert(func):

    def _operation(values, *args, **kwargs):
        if(db is None):
            raise ValueError('No db instance present...')
        else:
            val = func(db,values, *args, **kwargs)
            if(val):
                logging.info("Inserted item of page {} in main link {}".format(kwargs['i'],kwargs['url']))
              
    return _operation            


@custom_insert
def insert_db(db,values, **kwargs):

    result = db.rents.insert_one(values)
    return(result.acknowledged)
    

def preIndexcreate():
   resp =  db.rents.create_index([("uniqueId", ASCENDING )])  #TRYING TO CREATE I   NDEX ON THE UNIQUE HASH OF DJB2
   resp =  db.rents.create_index([("itemstreet", ASCENDING ),("itembhk", ASCENDING )])
  # print("resp is {}".format(resp)) 
   logging.info("Index created with info {}".format(resp)) 

def checkRecpresent(unique):
    # to check if record id present using unque id
    return db.rents.find_one({"uniqueId":unique}, {"itemlink":1 , "_id" :1})

def updateRec(mdict,idu):

    res = db.rents.update_one({"_id": idu},{'$set':mdict})
    logging.info("Update info - matched -- {} and modified -- {}".format(res.matched_count, res.modified_count))


def updateMeminfo():
    logging.info("Ram free after one item QUEUE over is  {} MB".format(psutil.virtual_memory().available/1024/1024))


def getallrec(limit):
    res =  db.rents.find({},{"itemimage":0, "_id":0, "uniqueId":0,"itemdeposit":0}).limit(int(limit))
    rs = []
    for r in res:
        rs.append(r)
    return rs 

def bhkareafiler(area,bhk,sort,limit):
    if(db is None):
        raise Exception("No db is found")
    else:
        if(sort=="ASC"):
            sortval = 1
        else:
            sortval = -1   
        if(bhk is not None):

            res = db.rents.find({"itemstreet":area,"itembhk":bhk},{"itemimage":0, "_id":0, "uniqueId":0,"itemdeposit":0}).sort([("itemrentprice",sortval)]).limit(limit)
        elif (bhk is None):
            res = db.rents.find({"itemstreet":area},{"itemimage":0, "_id":0, "uniqueId":0,"itemdeposit":0}).sort([("itemrentprice",sortval)]).limit(limit)
        else:
            return("problem with filterss")
        out = []
        for r in res:
            out.append(r)
        return out
    return None        

def areafiler(area,sort,limit):
    pass

    
    

    


