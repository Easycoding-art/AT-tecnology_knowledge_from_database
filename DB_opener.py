import pandas as pd
import psycopg2
import numpy as np

def normalize_data(file_path, name, password, *types) :
    con = psycopg2.connect(dbname=name, user="postgres", password=password, host="localhost")
    file = open(file_path, 'r')
    query = file.read()
    file.close()
    df = pd.read_sql(query, con)
    column_arr = []
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
    return df, column_arr

def create_dataset(df, class_parameter, train_percent, time_parameter = None) :
    df = df.sample(frac=1)#перемешиваем строки
    df_row_count = df.shape[0]
    cut_index = int((df_row_count/100)*train_percent)
    df_train = df.iloc [cut_index:]
    df_test = df.iloc [:cut_index]
    y_train = np.array(df_train[class_parameter].tolist())
    y_test = np.array(df_test[class_parameter].tolist())
    df_train.drop(columns = [class_parameter],axis = 1, inplace=True)
    df_test.drop(columns = [class_parameter],axis = 1, inplace=True)
    if time_parameter != None :
        t_train = np.array(df_train[time_parameter].tolist())
        t_test = np.array(df_test[time_parameter].tolist())
        df_train.drop(columns = [time_parameter],axis = 1, inplace=True)
        df_test.drop(columns = [time_parameter],axis = 1, inplace=True)
    x_train = df_train.to_numpy()
    x_test = df_test.to_numpy()
    train_data = {'x' : x_train, 'y' : y_train, 't' : t_train}
    test_data = {'x' : x_test, 'y' : y_test, 't' : t_test}
    return train_data, test_data


def parse_database(file_path, name, password, types, class_parameter, train_percent, time_parameter = None) :
    df, aliases = normalize_data(file_path, name, password, types)
    train, test = create_dataset(df, class_parameter, train_percent, time_parameter)
    return train, test, aliases
'''
df, arr = normalize_data('query.txt', 'avito3', '1234', 'int64')
print(df)
x, y, x_test, y_test = create_dataset(df, 'sum', 10)
print(x)
print(x_test)
'''