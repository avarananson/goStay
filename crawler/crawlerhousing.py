from flasked.crawler.crawler import CustomSpider
from flasked.djb2 import djb2
import re


base_dict_housing = {'url': 'https://housing.com/',

            'checklist': ['Flats','Rent']
    }
class Housing(CustomSpider):
    
    def getAlldetails(self, obj, idx):

        pagelems = obj.find_all("div", {"class": "css-xovbnn"})
        if(len(pagelems) >  0):
            #print("Extracting contents of page {}".format(idx))
            for elem in pagelems:
                maindict = {}
                maindict['itemwebsite'] = 'Housing.com'
                e = elem.find("div", {"data-q" : "result-data"})
                elink = e.find("a", {"data-q" : "title"})
                #print(elink)
                maindict['itemlink'] = elink['href']
            # print( maindict['itemlink'])
                maindict['itemtitle'] =  elink.text
                rm = obj.find("div", {"data-q" : "locality-info"})
                local = rm.find("div",{"data-q" : "locality-name"})
                maindict['itemlocality'] = local.text
                v = e.find("div",{"data-q" : "address"})
                street = v.find("a", {"class": "css-16drx2b"})
                maindict['itemstreet'] = street.text

                link = elem.find("div",{"class" : "css-1p99d2q"})
                #link = imageurldiv.find("div",{"class" : "nobrokerSlider"})
                if(link):
                    if(link.find("img")):
                        link = link.find("img")['src']
                    else:
                        link = None    
                else:
                    link = None
                maindict['itemimage'] =  link
                maindict['itembhk']  = ' '.join(self.getbhkdetails(maindict['itemtitle'])) 
                maindict['uniqueId'] =  str(djb2.hashed(maindict['itemlink']))
                maindict['itemdeposit'] = 0.0
                prices = e.find("div", {"data-q" : "price"})
                #pr1 = prices.find("span")
                if(prices is None):
                    depval = 0
                else:    
                    dep = re.sub('[^0-9.]', "", prices.text)
                    if( dep ==''):
                        depval = 0
                    else:
                        depval = float(dep) 
                maindict['itemrentprice'] = depval
                self.startdbinsertion(maindict,idx)

            print("    > Insertion completed for page {}".format(idx)) 
        else:
            self.done = True       


if( __name__ == "__main__"):
    hs = Housing.retSpider(base_dict_housing)
    hs.getinitialurls('css-64ag32')
    hs.processque(True)





# Ninenineacres.soup = BeautifulSoup(baseobj, 'lxml')
#         self.cities = []
#         parent = Ninenineacres.soup.find("div", { "class":"row"})
#         print(parent)
#         subs = parent.find_all("span", {"itemprop": "name"})