import pandas as pd
def set_classes(row):
 if row['actual_productivity'] < 0.3:
    val = 'low'
 elif row['actual_productivity'] < 0.6:
    val = 'normal'
 else :
    val = 'high'
 return val

def create_dataset() :
    df = pd.read_csv('garments_worker_productivity.csv')
    df['classes'] = df.apply (set_classes, axis=1)
    time_series = sorted(list(set(df['date'].to_list())))
    times = {time_series[i] : i for i in range(len(time_series))}
    df['time'] = df['date'].apply(lambda x: times.get(x))
    df.drop(['date','quarter','day', 'actual_productivity'], axis=1 , inplace=True)
    return df
print(create_dataset())