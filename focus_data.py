import matplotlib.pyplot as plt
from sklearn.svm import OneClassSVM
import warnings
import DBAccess

warnings.filterwarnings("ignore", category = DeprecationWarning)

# fokussiert Daten
def focus():
    train_vectors = []
    db = DBAccess.DB_access()
    db.open_db("Documents")
    data = db.load_documents()

    # Daten in train und test teilen
    test_data = []
    train_data = []
    i = 0
    for line in data:
        if i % 7 == 0:
            test_data.append(line)
        else:
            train_data.append(line)
        i += 1

    # vectoren raussuchen zum fokussieren
    for line in train_data:
        train_vectors.append(line.Vector)

    # one classSvm mit trainingsdaten trainieren
    clf = OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    clf.fit(train_vectors)

    # speichert die Werte der decision Funktion in der DB
    # später können Dokumente mit zu kleinem Wert aussortiert werden um DAten zu fokussieren
    for data in train_data:
        tmp = clf.decision_function(data.Vector)[0][0].item()
        db.save_decision(tmp, data.DocumentId)

    db.close_db()
