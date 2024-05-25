import dataset as ds
import DB_opener as db
import Random_forest_temporal as forest
from sklearn.metrics import classification_report
import knowledge_field as kf
import os

def start_experiment() :
    df = ds.create_dataset()
    column_arr = {}
    types = ['object']
    for data_type in types :
        type_df = df.dtypes[df.dtypes == data_type]
        columns = type_df.index.tolist()
        for column in columns :
            value_arr = df[column].tolist()
            classes = list(set(value_arr))
            class_dict = {}
            mask_dict = {}
            for i in range(len(classes)) :
                class_dict.update({i : classes[i]})
                mask_dict.update({classes[i] : i})
            column_arr.update({column : class_dict})
            df[column] = df[column].replace(mask_dict)
    train, test = db.create_dataset(df, 'classes', 10, 'time')
    clf = forest.RandomForestClassifier(n_estimators=200, max_depth=4)
    clf.fit(train.get('x'), train.get('y'), train.get('t'))
    # Прогнозируем метки классов 
    y_pred = clf.predict(test.get('x'))
    print(classification_report(test.get('y'), y_pred))
    #перевод в поле знаний
    field = kf.knowledge_field(df, column_arr, 'classes', 'time', clf, 200)
    file = open(f'test.kbs', 'w', encoding='utf-8')
    file.write(field)
    file.close()
    command = f'python -m at_krl atkrl-xml -i test.kbs -o test_TKB.xml -a test_Allen.xml'
    os.system(command)

start_experiment()