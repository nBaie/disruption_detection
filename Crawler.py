import logging
from urllib.request import urlopen
import exportToVector
from boilerpipe.extract import Extractor
import enchant
from bs4 import BeautifulSoup
from math import *
import gensim.models as g
dictionary = enchant.Dict("en_US")
logger = logging.getLogger(__name__)

# gibt alle Links zurück die auf der übergebenen URL vorkommen
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

# Funktion die boilerpipe Funktionalität kapselt
def extract (url):
    try:
        extractor = Extractor(extractor='ArticleExtractor', url=url)
        return extractor.getText().split()
    except:
        return []

# Crawler beginnt bei URL und speichert relevante Dokumente in DB bis maxPages erreicht ist
def spider(url, maxPages):
    numberVisited = 0
    linksClean = []
    links0 = []
    links1 = []
    links2 = []
    model = "model/my_model_d2v_py3.pkl"
    db = exportToVector.DB_access()

    f = open("example0.txt").read().split()
    for word in f:
        links0.append(word)
    f = open("example1.txt").read().split()
    for word in f:
        links1.append(word)
    f = open("example2.txt").read().split()
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

# speichert reinen Text einer URL in txt-Datei
def getTextFromLink(url,count):
    dataClean = extract(url)
    link = "example"+str(count)+".txt"
    file = open(link, "a")
    for line in dataClean:
        file.write(line)
        file.write(" ")
    file.write("\n")
    file.write("\n")
    file.close()

def square_rooted(x):
    return round(sqrt(sum([a * a for a in x])), 3)

# berechnet Ähnlichkeit von Vektoren
def cosine_similarity(x, y):
    numerator = sum(a * b for a, b in zip(x, y))
    denominator = square_rooted(x) * square_rooted(y)
    return round(numerator / float(denominator), 3)
