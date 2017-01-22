from urllib.request import urlopen


from boilerpipe.extract import Extractor
import enchant
from bs4 import BeautifulSoup
import gensim.models as g

import DBAccess

dictionary = enchant.Dict("en_US")
import logging
logger = logging.getLogger(__name__)

def getLinks( url ):
    # alle links die in dieser url vorkommen
    links = [url]
    # Remember the base URL which will be important when creating absolute URLs
    baseUrl = ""
    try:
        baseUrl = url[:url.index(".com")+4] #baseurl extrahieren und wenns nit klappt dann ist es eben so
    except:
        pass
    # Use the urlopen function from the standard Python 3 library
    try:
        response = urlopen(url)
    except:
        # wenns nicht klappt können keine links returned werden
        return []

    # Make sure that we are looking at HTML and not other things that
    # are floating around on the internet (such as
    # JavaScript files, CSS, or .PDFs for example)
    if 'text/html' in response.getheader('Content-Type') or 'text/plain' in response.getheader('Content-Type'):
        htmlBytes = response.read()
        #html parsen
        soup = BeautifulSoup(htmlBytes, 'html.parser')
        for link in soup.find_all('a'):
            if link.get('href') is not None:
                linkString = link.get('href')
                if linkString.startswith("/") or linkString.startswith("#"):
                    linkString = baseUrl + linkString #link zusammenbauen
                # falls es den link noch nicht gibt hinzufügen
                if linkString not in links:
                    links.append(linkString)
        return links
    else:
        return []

def extract (url):
    try:
        extractor = Extractor(extractor='ArticleExtractor', url=url)
        return extractor.getText().split()
    except:
        return []


def spider(url, maxPages):
    numberVisited = 0
    linksClean = []
    links0 = []
    links1 = []
    links2 = []
    model = "model/my_model_d2v_py3.pkl"
    db = DBAccess.DB_access()

    f = open("links0.txt").read().split()
    for word in f:
        links0.append(word)
    f = open("links1.txt").read().split()
    for word in f:
        links1.append(word)
    f = open("links2.txt").read().split()
    for word in f:
        links2.append(word)
    # load model
    myModel = g.Doc2Vec.load(model)

    try:
        print(numberVisited, "Visiting:", url)
        for link in getLinks(url):
            if "http://www" in link or "http://" in link or "https://www" in link and link not in linksClean:
                linksClean.append(link)
        print(" **Success!**")
    except:
        print(" **Failed!**")
    counter = 0
    db.open_db("Doc_Banking_zwei")

    # Vektoren aus bespieldkomunten ableiten. Sie bleiben so konstant und werden nur einmal berechnet
    b = myModel.infer_vector(links0, steps=5, alpha=0.005)
    c = myModel.infer_vector(links1, steps=5, alpha=0.005)
    d = myModel.infer_vector(links2, steps=5, alpha=0.005)

    while numberVisited < maxPages and linksClean != []:
        url = linksClean[counter]
        counter = counter + 1
        print("NEUE URL:")
        print(url)
        dataClean = extract(url)
        # print(dataClean)

        a = myModel.infer_vector(dataClean, steps=5, alpha=0.005)

        cos1 = cosine_similarity(a, b)
        cos2 = cosine_similarity(a, c)
        cos3 = cosine_similarity(a, d)
        #print(str(cos1) + " " + str(cos2) + " " + str(cos3))
        if cos1 > 0.7 and cos2 > 0.7 and cos3 > 0.7:
            print("relevantes Dokument gefunden (", numberVisited, "/", maxPages, ")")
            print(cos1)
            print(cos2)
            print(cos3)
            newlinks = getLinks(url)
            for link in newlinks:
                if link is not None and ("http://www" in link or "https://www" in link) and link not in linksClean:
                    linksClean.append(link)
            numberVisited = numberVisited + 1
            a=a.dumps()
            dataClean = " ".join(dataClean)
            db.save_new_document(a,dataClean,url)
    db.close_db()
# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def spiderDepr(url, maxPages):
    counter = False
    numberVisited = 0
    linksClean = []
    links0 = []
    links1 = []
    links2 = []
    model = "model/my_model_d2v_py3.pkl"
    f = open('stopwords.txt')
    stopwords = f.readlines()
    stopwords = [line.strip() for line in stopwords]
    f.close()
    f = open("links0.txt").read().split()
    for word in f:
        links0.append(word)
    f = open("links1.txt").read().split()
    for word in f:
        links1.append(word)
    f = open("links2.txt").read().split()
    for word in f:
        links2.append(word)
    # load model
    myModel = g.Doc2Vec.load(model)

    try:
        print(numberVisited, "Visiting:", url)
        for link in getLinks(url):
            if "http://www" in link or "https://www" in link and link not in linksClean:
                linksClean.append(link)
        print(" **Success!**")
    except:
        print(" **Failed!**")
        counter = 0
    while numberVisited < maxPages and linksClean != []:
        url = linksClean[counter]
        counter = counter + 1
        try:
            response = urlopen(url)
        except:
            continue
        dataClean = []
        if 'text/html' in response.getheader('Content-Type'):
            try:
                htmlBytes = response.read()
            except:
                continue
            try:
                htmlString = htmlBytes.decode("latin1")
            except UnicodeEncodeError as error :
                print(error)
            soup = BeautifulSoup(htmlString, 'html.parser')
            for elem in soup.findAll(['script', 'style']):
                elem.extract()
            data = soup.get_text()
            dataInWords = data.split()
            for word in dataInWords:
                if dictionary.check(word) == True:
                    if word.lower() not in stopwords:
                        dataClean.append(word.lower().replace('.','').replace("'",''))

            #print("NEUE URL:")
            print(url)
            #print(dataClean)

            a = myModel.infer_vector(dataClean, steps=5, alpha=0.005)
            b = myModel.infer_vector(links0, steps=5, alpha=0.005)
            c = myModel.infer_vector(links1, steps=5, alpha=0.005)
            d = myModel.infer_vector(links2, steps=5, alpha=0.005)
            cos1 = cosine_similarity(a, b)
            cos2 = cosine_similarity(a, c)
            cos3 = cosine_similarity(a, d)
            print(str(cos1) + " " + str(cos2) + " "  + str(cos3))
            if cos1 > 0.7 and cos2 > 0.7 and cos3 > 0.7:
                print("relevantes Dokument gefunden (" , numberVisited,"/",maxPages,")")
                print(cos1)
                print(cos2)
                print(cos3)
                newlinks = getLinks(url)
                for link in newlinks:
                    if link is not None and ("http://www" in link or "https://www" in link) and link not in linksClean:
                        linksClean.append(link)
                numberVisited = numberVisited + 1
                file = open("newfile_banking.txt", "a")
                #file.write(str(cos1) + ", " + str(cos2) + ", " + str(cos3))
                for line in dataClean:
                    file.write(line)
                    file.write(" ")
                file.write("\n")
                #file.write("\n")
                file.close()

def getTextFromLinkDepr(url,count):
    response = urlopen(url)
    f = open('stopwords.txt')
    stopwords = f.readlines()
    stopwords = [line.strip() for line in stopwords]
    f.close()
    dataClean = []
    if 'text/html' in response.getheader('Content-Type'):
        htmlBytes = response.read()
        try:
            htmlString = htmlBytes.decode("latin1")
        except UnicodeEncodeError as error:
            print(error)
        soup = BeautifulSoup(htmlString, 'html.parser')
        for elem in soup.findAll(['script', 'style']):
            elem.extract()
        data = soup.get_text()
        dataInWords = data.split()
        for word in dataInWords:
            if dictionary.check(word) == True:
                if word.lower() not in stopwords:
                    dataClean.append(word.lower().replace('.', '').replace("'", ''))
    link="links"+str(count)+".txt"
    file = open(link, "a")
    for line in dataClean:
       file.write(line)
       file.write(" ")
    file.write("\n")
    file.write("\n")
    file.close()

def getTextFromLink(url,count):
    dataClean = extract(url)

    link="links"+str(count)+".txt"
    file = open(link, "a")
    for line in dataClean:
       file.write(line)
       file.write(" ")
    file.write("\n")
    file.write("\n")
    file.close()

from math import *


def square_rooted(x):
    return round(sqrt(sum([a * a for a in x])), 3)


def cosine_similarity(x, y):
    numerator = sum(a * b for a, b in zip(x, y))
    denominator = square_rooted(x) * square_rooted(y)
    return round(numerator / float(denominator), 3)