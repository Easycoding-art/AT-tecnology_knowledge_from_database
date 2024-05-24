column_list = [f'column_{i}' for i in range(20)]
aliases = {'result':{0: 'high', 1: 'medium', 2: 'low'}}
string = '1685366492288 [label="time = 7, X[6] <= 21.0"]'
string2 = '1685366492288 -> 1685366492096'
string3 = '1685366492096 [label=0]'
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
def vote(start_node, leave, intervals, unparsed_arr, start_time) :
    path = [leave[0]]
    arr = list(filter(lambda x: '->' in x, unparsed_arr))
    pointers = list(map(lambda x: x.split(' -> '), arr))
    parent = ''
    i = 0
    while True :
        parent_child = list(filter(lambda x: x[1] == path[i], pointers))
        parent = parent_child[0][0]
        path.append(parent)
        if parent == start_node :
            break
        i+=1
    path.reverse()
    print(intervals)
    conditions = []
    for current_node in path[:len(path)-1] :
        condition = eval(intervals.get(current_node)[0][1].replace('current_time', 
                                                             str(start_time)))
        conditions.append(condition)
    if not all(conditions) == True :
        file = open('rule_template.txt', 'r', encoding='utf-8')
        rule = file.read()
        rule = rule.replace('name', leave[0])
        rule = rule.replace('class', leave[1])
        #intervals.get(current_node)[0][1]
        file.close()
        return rule
    else :
        return None
    print(path)
node = get_node_info(string, column_list)
leave = get_leave_info(string3, aliases, 'result')
interval = get_interval(node)
path = vote('1685366492288', leave, interval, [string, string2, string3], 0)
print(path)
#interval = get_interval(node)
#print(interval)