import logging
import Crawler
import focus_data
import analyse

logger = logging.getLogger(__name__)

# Beispiel Dokumente für banking runterladen
Crawler.getTextFromLink("https://www.quora.com/How-do-banks-make-money", 0)
Crawler.getTextFromLink("http://lecocqassociate.com/news/structuring-traditional-swiss-private-bank/", 1)
Crawler.getTextFromLink("http://fintechprofile.com/2016/05/13/traditional-banking-business-model-vs-focusing-consumer-whats-next/", 2)

# startet crawling von jeweiligen Seeds
Crawler.spider("http://lecocqassociate.com/news/structuring-traditional-swiss-private-bank/", 1500)
Crawler.spider("http://www.chambers-associate.com/practice-areas/banking-and-finance", 1500)

# fokussiert Daten
focus_data.focus()

# startet Analyse und Auswertung falls Testdaten gelabelt sind
analyse.analyse()