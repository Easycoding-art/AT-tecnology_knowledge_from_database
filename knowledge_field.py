import pandas as pd
import numpy as np
import dataset as ds
import DB_opener as db
import Random_forest_temporal as forest
from sklearn.metrics import classification_report
def get_attribute(string) :
    pass
def get_event(time) :
    pass
def get_counter_attribute(string) :
    pass
def build_text(attributes, events, counter_attributes, rules, intervals) :
    pass
def knowledge_field(df, aliases, classes, clf, n) :
    feature_names = list(df)
    times = sorted(list(set(df['time'].to_list())))
    class_names_aliases = list(set(df[classes].to_list()))
    class_names = list(map(lambda x: aliases.get(classes).get(int(x)), class_names_aliases))
    attributes = list(map(lambda x: get_attribute(x), feature_names))
    events = list(map(lambda x: get_event(x), times))
    counter_attributes = list(map(lambda x: get_counter_attribute(x), class_names))
    rules = []
    intervals = []
    for i in range(n) :
        interval, rule = parse_tree(str(clf.estimators[i].visualize_tree()),
                        feature_names, aliases, classes)
        rules = [*rules, *rule]
        intervals = [*intervals, *interval]
    text = build_text(attributes, events, counter_attributes, rules, intervals)
    return text

def get_node_info(string, column_list) :
    string = string.replace(' ', '')
    string = string.replace('label="time=', '')
    string = string.replace('X[', '')
    string = string.replace('"]', '')
    string = string.replace('<=', '')
    string = string.replace('[', '#')
    string = string.replace(']', '#')
    string = string.replace(',', '#')
    array = string.split('#')
    array[2] = column_list[int(array[2])]
    return (array[0], array[2], array[3], array[1])

def get_leave_info(string, aliases, class_column) :
    string = string.replace('[label=', '')
    string = string.replace(']', '')
    array = string.split()
    array[1] = aliases.get(class_column).get(int(array[1]))
    return (array[0], array[1])
def get_interval(node) :
    node_time = node[3]
    trashold = node[2]
    value = node[1]
    plus_start = f'current_time == {node_time} + start_time and {value} < {trashold}'
    plus_end = f'current_time == {node_time} - 1'
    minus_start = f'current_time == {node_time} and {value} >= {trashold}'
    minus_end = f'current_time == {node_time} - 1'
    return{node[0]: ((plus_start, plus_end), (minus_start, minus_end))}
def parse_tree(string, feature_names, class_aliases, class_column) :
    class_counter = {v: 0 for v in class_aliases.get(class_column).keys()}
    string = string.replace('digraph {', '')
    string = string.replace('}\n', '')
    arr = string.split('\n\t')
    arr.pop(0)
    arr[len(arr)-1] = arr[len(arr)-1].replace('\n', '')
    node_list = [node.split()[0] for node in arr]
    node_names = list(set(node_list))
    nodes = [get_node_info(arr[node_list.index(node_name)], feature_names) 
            for node_name in node_names if 'time' in arr[node_list.index(node_name)]]
    leaves = [get_leave_info(arr[node_list.index(node_name)], class_aliases, class_column) 
            for node_name in node_names if 'time' not in arr[node_list.index(node_name)]]
    intervals = {}
    for node in nodes :
        intervals.update(get_interval(node))
    for leave in leaves :
        class_counter.update(vote(start_node, leave, intervals, arr))
    print(nodes)
    return nodes

def start_experiment() :
    df = ds.create_dataset()
    column_arr = []
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
            column_arr.append({column : class_dict})
            df[column] = df[column].replace(mask_dict)
    train, test = db.create_dataset(df, 'classes', 10, 'time')
    print(train)
    clf = forest.RandomForestClassifier(n_estimators=200, max_depth=4)
    clf.fit(train.get('x'), train.get('y'), train.get('t'))
    # Прогнозируем метки классов 
    y_pred = clf.predict(test.get('x'))
    print(classification_report(test.get('y'), y_pred))
    #перевод в поле знаний
    field = knowledge_field(df, column_arr, 'classes', clf, 200)
start_experiment()
