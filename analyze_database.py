import os
import DB_opener as db
import Random_forest_temporal as forest
from sklearn.metrics import classification_report
import knowledge_field as kf
import DB_opener as dbo

def create_field(query_text, db_name, db_password, n_estimators,
                max_depth, name, target, time_name, percent=0, *types) :
    df, arr = dbo.normalize_data(query_text, db_name, db_password, *types)
    train, test = db.create_dataset(df, target, percent, time_name)
    clf = forest.RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    clf.fit(train.get('x'), train.get('y'), train.get('t'))
    if percent != 0 :
        # Прогнозируем метки классов 
        y_pred = clf.predict(test.get('x'))
        return classification_report(test.get('y'), y_pred)
    else :
        #перевод в поле знаний
        field = kf.knowledge_field(df, arr, target, time_name, clf, n_estimators)
        file = open(f'{name}.kbs', 'w', encoding='utf-8')
        file.write(field)
        file.close()
        command = f'python -m at_krl atkrl-xml -i {name}.kbs -o {name}_TKB.xml -a {name}_Allen.xml'
        os.system(command)