import pandas as pd

def knowledge_field(df, classes) :
    column_list = df.columns.values.tolist()
    times = sorted(list(set(df['time'].to_list())))
    class_names = list(set(df[classes].to_list()))
    counter = {name:0 for name in class_names}
    
