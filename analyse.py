from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
import warnings
import DBAccess
warnings.filterwarnings("ignore", category=DeprecationWarning)


# gibt Label zu einer DocId zurück
def getLabelbyId( id, docs):
    for doc in docs:
        if doc.DocumentId == id:
            return doc.Text


# schreibt Werte aus labels.csv in DB für späteren Gebrauch
def write_labels_to_db():
    db = DBAccess.DB_access()
    db.open_db("labels")
    f = open("labels.csv").read().split("\n")

    for line in f:
        tmp = line.split(",")
        db.saveLabeledResult(tmp[0], tmp[1])


# führt analyse der Daten.
#  durch Falls True positives und so weiter gezählt werden sollen muss eine Tabelle mit Labeln zum Testset erstellt werden
def analyse():
    # Daten aus DB laden
    db = DBAccess.DB_access()
    db.open_db("Documents")
    train = db.load_documents_dec()
    test = db.load_test_data()
    db.close_db()

    train_vectors = []

    # train_vectors füllen
    for line in train:
        if len(line.Text) > 3000:
            train_vectors.append(line.Vector)

    # One Class SVM trainieren
    clf = OneClassSVM(nu=0.025, kernel="rbf", gamma=0.1)
    clf.fit(train_vectors)

    # true positives zählen
    tp = 0
    # false negatives zählen
    fn = 0
    # false positive
    fp = 0
    # true negative
    tn = 0

    # gelabelte Daten laden falls es welche gibt
    labels = None
    try:
         db.open_db("interessant")
         labels = db.load_labels()
         db.close_db()
    except:
        pass

    #model mit testdaten testen
    for line in test:
        if len(line.Text)>3000:     #Bedingung für Mindestlänge der Dokumente
            print("Prediction: ", clf.predict(line.Vector), " DocID: ", line.DocumentId, " Disruption: ", (clf.predict(line.Vector)<0), ";", line.URL)
            # falls es gelabelte Dokumente gibt, werden tp, fn,fp u tn gezählt
            if labels is not None and len(labels) > 0:
                if clf.predict(line.Vector) < 0 and getLabelbyId(line.DocumentId, labels) == 'interessant':
                    tp += 1
                elif clf.predict(line.Vector) > 0 and getLabelbyId(line.DocumentId, labels) == 'interessant':
                    fn += 1
                elif clf.predict(line.Vector) < 0 and getLabelbyId(line.DocumentId, labels) == 'nicht':
                    fp += 1
                elif clf.predict(line.Vector) > 0 and getLabelbyId(line.DocumentId, labels) == 'nicht':
                    tn += 1
    try:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1score = 2 * tp / (2 * tp + fp + fn)
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        print("precision: ", precision, " recall: ", recall, " f1score: ", f1score, " accuracy: ", accuracy)
    except:
        pass



    #ISOLATION FOREST CLASSIFICATION
    tp = 0
    fn = 0
    fp = 0
    tn = 0
    classifier = IsolationForest()
    classifier.fit(train_vectors)
    print("Isolation Forest Classification")
    #model mit testdaten testen
    for line in test:
        if len(line.Text) > 3000:
            print("Prediction: ", classifier.predict(line.Vector), " DocID: ", line.DocumentId, " Disruption: ", (classifier.predict(line.Vector)<0), ";", line.URL)
            if labels is not None and len(labels) > 0:
                if classifier.predict(line.Vector) < 0 and getLabelbyId(line.DocumentId,labels) == 'interessant':
                    tp += 1
                elif classifier.predict(line.Vector) > 0 and getLabelbyId(line.DocumentId,labels) == 'interessant':
                    fn += 1
                elif classifier.predict(line.Vector) < 0 and getLabelbyId(line.DocumentId,labels) == 'nicht':
                    fp += 1
                elif classifier.predict(line.Vector) > 0 and getLabelbyId(line.DocumentId,labels) == 'nicht':
                    tn += 1

    try:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1score = 2 * tp / (2 * tp + fp + fn)
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        print("precision: ",precision," recall: ",recall, " f1score: ",f1score, " accuracy: ", accuracy)
    except:
        pass

