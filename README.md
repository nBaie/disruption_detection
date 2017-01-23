# disruption_detection
web mining application for competitor analysis and disruption detection

This project contains the code written for the thesis: "web mining applications for competitor analysis and disruption detection" 

To get the code running the following steps have to be executed (explanation for python 3.4):
===============================================================

1. Check-out the repository

2. Get pre-trained Doc2Vec model [English Wikipedia (1.4GB)](https://ibm.box.com/s/3f160t4xpuya9an935k84ig465gvymm2)

3. Put the downloaded files for the model into /model/

4. Execute the SQL-script (/SQL/create_table.sql) on a mysql database  
    4.1 The Connection for the DB can be found in DBAccess starting from line 13

5. Install the following packages for python: enchant, bs4, gensim, sklearn, pymysql

6. Download [Boilerpipe sources](https://github.com/misja/python-boilerpipe)  
    6.1 Install JPype1-py3  
    6.2 Replace setup.py by our uploaded setup.py(Boilerpipe/setup.py)  
    6.3 Run Setup.py (sudo python setup.py install)  
    6.4 Go to Crawler.py, press f3 on Extractor in line5 to reach the __init__.py of the extractor class  
    6.5 In that file replace "unicode" in line 41,44,45 with "str"  

7. Adapt main.py to your topic or just run it

