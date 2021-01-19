from bs4 import BeautifulSoup
import requests
from collections import deque
from flasked.store import mongoprep
from flasked.djb2 import djb2
import re

base_dict = {'url': 'https://www.nobroker.in',

            'checklist': ['Flats','rent']
    }


class CustomSpider:
    itemlimit = 50
    
    bhks = [['1','BHK'],['2','BHK'],['3','BHK'],['4','BHK'],['2.5', 'BHK'],['2.5','RK'],['4+','BHK'], ['1','RK'],[
        '2','RK'],['3','RK'],['4','RK'],['4+','RK'], ['5','BHK'],['5','RK']]

    def __init__(self, url , checklst, *args, **kwargs):
        self.col = 'rents'
        self.url = url 
        self.checklist = checklst
        self.done = False
        if(args):
            print("args present are {}".format(args)) 
        print("Initaliting mongo setup")    
        str = mongoprep.initiatedb() 
        if(self.col not in mongoprep.getcollnames()):
            mongoprep.createcollection(self.col)
        else:
            print("Collection {} already in databse".format(self.col))    
        print(' Current collections present in databse are {}'.format(mongoprep.getcollnames()))  
        mongoprep.preIndexcreate()

    @classmethod
    def retSpider(cls, dicto, *args, **kwargs):
        return cls(dicto['url'],dicto['checklist'])

    def initializeQue(self):
        self.urlque = deque()
        for item in self.allurls:
            self.urlque.append(item['url'])

        print("len of queue",len(self.urlque))
        #print("ttttt",self.urlque)

    @staticmethod
    def getbhkdetails(title):
        vals = title.upper().split()
        #print(vals)
        for bhks in CustomSpider.bhks:
            if(all(bk in vals for bk in bhks)):
                return bhks

        return [""]

    def cleanurls(self):
        for  value  in reversed((self.allurls)) :
            if( not (all(val in value['text'].split() for val in self.checklist))):
                self.allurls.remove(value)
        print(len(self.allurls))
        self.initializeQue()

    def getinitialurls(self, attr):
        page = requests.get(self.url).text
        soup = BeautifulSoup(page,'lxml')

        elems = soup.find_all('a', class_= attr)
        self.allurls = []
        for elem in elems :
            ul = elem['href']
            txt = elem.text
            #print(ul,txt)
            self.allurls.append({'text': txt, 'url':ul})

        self.cleanurls()

    def doDetcheck(self,mdct, check, idx):
        if(mdct["itemlink"] == check["itemlink"]):
            mongoprep.updateRec(mdct, check["_id"])
        else:
            mongoprep.insert_db(mdct, i = idx, url = self.curr_url)


    def startdbinsertion(self, maindict, idx):

        check = mongoprep.checkRecpresent(maindict['uniqueId'])
        if((check is None)):
            mongoprep.insert_db(maindict, i = idx, url = self.curr_url)
        else:
            self.doDetcheck(maindict, check, idx)    

    def getAlldetails(self, obj, idx):

        pagelems = obj.find_all("div", {"class": "card"})
        if(len(pagelems) >  0):
            #print("Extracting contents of page {}".format(idx))
            for elem in pagelems:
                maindict = {}
                maindict['itemwebsite'] = 'NoBroker'
                e = elem.find("a", {"class" : "card-link-detail"})
                maindict['itemlink'] = e['href']
            # print( maindict['itemlink'])
                maindict['itemtitle'] =  e['title']
            # print(maindict['itemtitle'] )
                street = elem.find("span",{"itemprop" : "streetAddress"})
                maindict['itemstreet'] = street.text
            # print(maindict['itemstreet'])
                local = elem.find("span",{"itemprop" : "addressLocality"})
                maindict['itemlocality'] = local.text
            # print(maindict['itemlocality'])
                imageurldiv = elem.find("div",{"class" : "card-image"})
                link = imageurldiv.find("div",{"class" : "nobrokerSlider"})
                if(link):
                    link = link.find("a")['data-src']
                else:
                    link = None
                maindict['itemimage'] =  link
                maindict['itembhk']  = ' '.join(self.getbhkdetails(maindict['itemtitle']))         
                maindict['uniqueId'] =  str(djb2.hashed(maindict['itemlink']))
                #print(maindict)
                prices = elem.find_all("div",{"itemprop" : "valueReference"})
                pr1 = prices[1].find('span')
                if(pr1 is None):
                    depval = 0
                else:    
                    dep = re.sub('[^0-9.]', "", pr1.text)
                    if( dep ==''):
                        depval = 0
                    else:
                        depval = float(dep)   
                maindict['itemdeposit'] = depval
                pr2 = prices[2].find('span')
                if(pr2 is None):
                    rent =0
                else:    
                    ren = re.sub('[^0-9.]', "", pr2.text)
                    if( ren ==''):
                        rent = 0
                    else:
                        rent = float(ren)   
                maindict['itemrentprice'] = rent
                #print(maindict)
                self.startdbinsertion(maindict,idx)

            print("    > Insertion completed for page {}".format(idx)) 
        else:
            self.done = True       

    def processque(self,housing):

        for _ in range(7):
            self.urlque.popleft()

        while self.urlque:
            ul = self.urlque.popleft()
            if(housing):
                ul = 'https://housing.com'+ ul
            self.curr_url = ul
            print("Main url in queue is {}".format(ul))
            req = requests.get(ul).text
            soupobj = BeautifulSoup(req,'lxml')
            hlink = soupobj.find("link",{'rel' : "next"})['href']
            # if(housing):
            #     hlink = 'https://housing.com'+hlink 
            count = 1
            while count <= CustomSpider.itemlimit :
                if(self.done):
                    self.done = False
                    break
                if(count > 1):
                    print(hlink)
                    hlink = hlink[:len(hlink)-len(str(count-1))]+str(count)
                    subreq = requests.get(hlink).text
                    soupobj = BeautifulSoup(subreq,'lxml')
                if(count > 1) :   
                    print(" --> Initial sub url is {}".format(hlink))    
                self.getAlldetails(soupobj,count) 
                soupobj.decompose()               
                
                count = count +1
            mongoprep.updateMeminfo()    


if (__name__ == "__main__"):
    cus  =  CustomSpider.retSpider(base_dict)
    cus.getinitialurls('sitemap-footer-content')
    cus.processque(False)
    

