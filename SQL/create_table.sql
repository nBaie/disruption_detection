create SCHEMA disruption_detection;
commit;

create table Documents (
    idDocuments INT NOT NULL AUTO_INCREMENT,
    vector blob NOT NULL,
    text mediumtext NOT NULL,
    decision_value float,
    url mediumtext);

--keine Text-Duplikate einfügen
ALTER IGNORE TABLE `Documents`
ADD UNIQUE INDEX (`text`);