create SCHEMA disruption_detection;
commit;

create table disruption_detection.Documents (
    idDocuments INT NOT NULL AUTO_INCREMENT,
    vector blob NOT NULL,
    text mediumtext NOT NULL,
    decision_value float,
    url mediumtext,
    PRIMARY KEY (`idDocuments`));
