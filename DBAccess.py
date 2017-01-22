import numpy
import pymysql.cursors
import Beans

class DB_access:
    connection = None
    db_Name = ""

    # öffnen einer Connection zur mysql db
    # alle operationen auf dieser Connection werden auf der übergebenen Tabelle ausgeführt
    def open_db(self, db_name):
        self.db_Name = db_name
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password='',
                                          db='disruption_detection',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
    # schließen der connection
    def close_db(self):
        self.connection.close()

    def save_new_document(self, vector, text, url):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO " + self.db_Name + " (`vector`, `text`, `url`) VALUES (%s, %s, %s)"
            cursor.execute(sql, ( vector, text, url))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self.connection.commit()

    #
    def save_decision(self, decision_value, id):

        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "UPDATE " + self.db_Name + " SET decision_value = %s WHERE idDocuments = %s"
            cursor.execute(sql, (decision_value,id))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self.connection.commit()

    # gibt alle Dokumente zurück
    def load_documents(self):
        docs = []
        with self.connection.cursor() as cursor:
            sql = "select * from " + self.db_Name
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                vector = numpy.loads(row['vector'])
                doc = Beans.doc_bean(row['idDocuments'], vector, row['text'], row["decision_value"], row["url"])
                docs.append(doc)
        return docs

    # gibt alle Dokumente zurück dessen decision_value über bestimmtem Wert liegt
    def load_documents_dec(self):
        docs = []
        with self.connection.cursor() as cursor:
            sql = "select * from "+ self.db_Name +" WHERE decision_value > 0"
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                vector = numpy.loads(row['vector'])
                doc = Beans.doc_bean(row['idDocuments'], vector, row['text'], row["decision_value"], row["url"])
                docs.append(doc)
        return docs

    def load_test_data(self):
        docs = []
        with self.connection.cursor() as cursor:
            sql = "select * from "+ self.db_Name +" WHERE decision_value is Null"
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                vector = numpy.loads(row['vector'])
                doc = Beans.doc_bean(row['idDocuments'], vector, row['text'], row["decision_value"], row["url"])
                docs.append(doc)
        return docs

    def load_doc_by_id(self,idList):
        docs = []
        with self.connection.cursor() as cursor:
            for id in idList:
                sql = "select * from "+ self.db_Name +" WHERE idDocuments = (%s)"
                cursor.execute(sql,(id))
                results = cursor.fetchall()
                for row in results:
                    vector = numpy.loads(row['vector'])
                    doc = Beans.doc_bean(row['idDocuments'], vector, row['text'], row["decision_value"], row["url"])
                    docs.append(doc)
        return docs

    def get_url_by_id(self, id):
        with self.connection.cursor() as cursor:
            sql = "select url from " + self.db_Name + " WHERE idDocuments = (%s)"
            cursor.execute(sql, (id))
            results = cursor.fetchall()
            for row in results:
                return row['url']

    def saveLabeledResult(self, id_doc, label):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO " + self.db_Name + " (`idinteressant`, `text`) VALUES (%s, %s)"
            cursor.execute(sql, (id_doc, label))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self.connection.commit()

    # lädt manuelle Labels
    def load_labels(self):
        docs = []
        with self.connection.cursor() as cursor:
            sql = "select * from " + self.db_Name
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                doc = Beans.doc_interessant(row['idinteressant'], row['text'])
                docs.append(doc)
        return docs