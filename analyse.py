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


# führt analyse der Daten durch
def analyse():
    # Daten aus DB laden
    db = DBAccess.DB_access()
    db.open_db("Documents")
    train = db.load_documents_dec()
    test = db.load_test_data()
    db.close_db()

    doc_text = []
    train_vectors = []
    test_data = []
    train_data2 = []
    anzahl_disruption = 0
    anzahl_doc_gt_3000 = len(train)
    k = len(train)

    # train_vectors füllen
    for line in train:
        if len(line.Text) > 3000:
            train_vectors.append(line.Vector)

    # One Class SVM trainieren
    clf = OneClassSVM(nu=0.025, kernel="rbf", gamma=0.1)
    clf.fit(train_vectors)

    #
    disruptions = []
    # true positives zählen
    tp = 0
    # false negatives zählen
    fn = 0
    # false positive
    fp = 0
    # true negative
    tn = 0

    # gelabelte Daten laden
    db.open_db("interessant")
    labels = db.load_labels()
    db.close_db()

    anzahl_doc_gt_3000 = 0
    anzahl_disruption = 0
    for line in train:
        if len(line.Text) > 3000:
            print("Prediction: ", clf.predict(line.Vector), " DocID: ", line.DocumentId, " ", (clf.predict(line.Vector)>0), ";", line.URL)
            if clf.predict(line.Vector) < 0:
                anzahl_disruption += 1
            anzahl_doc_gt_3000 += 1
    print("Anzahl Disruption:", anzahl_disruption, anzahl_doc_gt_3000)
    #

    anzahl_disruption=0
    for line in train:
        print("Prediction: ", clf.predict(line.Vector), " DocID: ", line.DocumentId, " ", (clf.predict(line.Vector) > 0),
              ";", line.URL)
        if clf.predict(line.Vector) < 0:
            anzahl_disruption += 1

    print("Anzahl Disruption:", anzahl_disruption, len(train))
    #model mit testdaten testen
    for line in test:
        if len(line.Text)>3000:
            print("Prediction: ", clf.predict(line.Vector), " DocID: ", line.DocumentId, " ", (clf.predict(line.Vector)>0), ";", line.URL)
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

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1score = 2*tp/(2*tp+fp+fn)
    accuracy = (tp+tn)/(tp+fp+fn+tn)

    print("precision: ", precision, " recall: ", recall, " f1score: ", f1score, " accuracy: ", accuracy)


    #ISOLATION FOREST CLASSIFICATION
    tp = 0
    fn = 0
    fp = 0
    tn = 0
    classifier = IsolationForest()
    classifier.fit(train_vectors)

    #model mit testdaten testen
    for line in test:
        if len(line.Text) > 3000:
            print("Prediction: ", classifier.predict(line.Vector), " DocID: ", line.DocumentId, " ", (classifier.predict(line.Vector)>0), ";", line.URL)
            if classifier.predict(line.Vector) < 0 and getLabelbyId(line.DocumentId,labels) == 'interessant':
                tp += 1
            elif classifier.predict(line.Vector) > 0 and getLabelbyId(line.DocumentId,labels) == 'interessant':
                fn += 1
            elif classifier.predict(line.Vector) < 0 and getLabelbyId(line.DocumentId,labels) == 'nicht':
                fp += 1
            elif classifier.predict(line.Vector) > 0 and getLabelbyId(line.DocumentId,labels) == 'nicht':
                tn += 1

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1score = 2*tp/(2*tp+fp+fn)
    accuracy = (tp+tn)/(tp+fp+fn+tn)

    print("precision: ",precision," recall: ",recall, " f1score: ",f1score, " accuracy: ", accuracy)

    #vectors_train=[]
    #vectors_test=[]
    #tp = 0
    #fn = 0
    #fp = 0
    #tn = 0
    #documents=g.Doc2Vec.TaggedLineDocument(doc_text)

    #model = g.Doc2Vec(documents=doc_text, size=100, window=8, min_count=5, workers=4)
    #for value in data:
    #    vectors_train.append(model.infer_vector(value.Text))
    #for value in data2:
    #    vectors_test.append(model.infer_vector(value.Text))
    #
    # clf1 = OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    # clf1.fit(vectors_train)
    # s=0
    # for line in data2:
    #     print("Prediction: ", clf1.predict(vectors_test[s]), " DocID: ", line.DocumentId, " ", (clf1.predict(vectors_test[i])>0), ";", line.URL)
    #     if clf1.predict(vectors_test[s]) < 0 and getLabelbyId(line.DocumentId,interessant) == 'interessant':
    #         tp += 1
    #     elif clf1.predict(vectors_test[s]) > 0 and getLabelbyId(line.DocumentId,interessant) == 'interessant':
    #         fn += 1
    #     elif clf1.predict(vectors_test[s]) < 0 and getLabelbyId(line.DocumentId,interessant) == 'nicht':
    #         fp += 1
    #     elif clf1.predict(vectors_test[s]) > 0 and getLabelbyId(line.DocumentId,interessant) == 'nicht':
    #         tn += 1
    #
    # precision = tp/(tp+fp)
    # recall = tp/(tp+fn)
    # f1score = 2*tp/(2*tp+fp+fn)
    # accuracy = (tp+tn)/(tp+fp+fn+tn)
    #
    # print("precision: ",precision," recall: ",recall, " f1score: ",f1score, " accuracy: ", accuracy)
    # vectors_train=[]