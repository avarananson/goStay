from flasked.crawler.crawler import CustomSpider
from flasked.djb2 import djb2
from bs4 import BeautifulSoup
import re
import requests

base_dict_99acres = {'url': 'https://www.99acres.com/',

            'checklist': ['Flats','Rent']
    }

class Ninenineacres(CustomSpider):
    
    soup = None
    def getcitieslist(self):

        print("initial url is",self.url)
        baseobj = requests.get(self.url).text
        Ninenineacres.soup = BeautifulSoup(baseobj, 'lxml')
        self.cities = []
        parent = Ninenineacres.soup.find("div", { "class":"nationalLists"})
        subs = parent.find_all("a", {"class": "cityLinkInHeader"})
        for elem in subs :
            if(not("/" in elem.get_text()) and (not (elem.get_text() == "All India"))):
                self.cities.append(elem.get_text().strip().lower())

        self.cities.insert(0,'delhi-ncr')
        print("Total cities found {}".format(len(self.cities)))

    def getalltheurls(self):
        #urltemp = "https://www.99acres.com/property-for-rent-in-{}-ffid".format()
        self.allurls = []
        for elems in self.cities:
             urltemp = "https://www.99acres.com/property-for-rent-in-{}-ffid".format(elems)
             self.allurls.append({'text': "Flats for Rent in {}".format(elems.capitalize()), 'url':urltemp})
        print(self.allurls)   
        self.cleanurls()     

    def getAlldetails(self, obj, idx):

        pagelems = obj.find_all("div", {"class": "srpTuple__srpTupleBox"})
        print(len(pagelems))
        if(len(pagelems) >  0):
            #print("Extracting contents of page {}".format(idx))
            for elem in pagelems:
                maindict = {}
                maindict['itemwebsite'] = '99acres'
                d = elem.find("div",{"class":"srpTuple__tupleDetails"})
              #  print(d)
                title  = d.find("a",{"class":"srpTuple__propertyName"})
                #title1 = title.find("a",{"id":"srp_tuple_property_title"})
                #print(title.text)
               # print(title['href'])
                maindict['itemlink'] = title['href']
                maindict['itemtitle'] = title.text
                x = d.find("td",{"id":"srp_tuple_price"})
                if(x is not None and ("month" in x.text)):
                    depval = re.sub('[^0-9.]', "", x.text.split("month")[0])
                else:
                    depval = 0    
                    
               
                maindict['itemrentprice'] = float(depval) 
                maindict['itemdeposit'] = 0.0  
                r = d.find("td",{"id":"srp_tuple_bedroom"}) 
                #print(r.text)
                maindict['itembhk']  = ' '.join(self.getbhkdetails(r.text))     
                print(maindict['itembhk']) 

            print("    > Insertion completed for page {}".format(idx)) 
        else:
            self.done = True       





if( __name__ == "__main__"):
    acres = Ninenineacres.retSpider(base_dict_99acres)
    acres.getcitieslist()
    acres.getalltheurls()
    acres.processque(False)
    # hs.getinitialurls('css-64ag32')
    # hs.processque(True)

