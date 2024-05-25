def get_attribute(string) :
    file = open('atribute_template.txt', 'r', encoding='utf-8')
    template = file.read()
    file.close()
    text = template.replace('name', string)
    text = text.replace('type', 'ЧИСЛО')
    return text

def get_event(time) :
    file = open('event_template.txt', 'r', encoding='utf-8')
    template = file.read()
    file.close()
    text = template.replace('n', str(time))
    return text

def get_result_rules(class_names, n) :
    full_atrubutes = list(map(lambda x: f'Счетчик.{x}', class_names))
    sum_result = ' + '.join(full_atrubutes)
    file = open('result_rule_template.txt', 'r', encoding='utf-8')
    template = file.read()
    file.close()
    result_rules = []
    for atribute_name in full_atrubutes :
        other_classes = list(filter(lambda x: x != atribute_name, full_atrubutes))
        classes_condition = list(map(lambda x: f'{x} < {atribute_name}', other_classes))
        conditions = ' & '.join(classes_condition)
        text = template.replace('class_sum', sum_result)
        text = text.replace('condinions', conditions)
        text = text.replace('class_name', atribute_name.replace('Счетчик.', ''))
        text = text.replace('result', atribute_name.replace('Счетчик.', ''))
        text = text.replace('n_estimators', str(n))
        result_rules.append(text)
    return result_rules

def build_text(attributes, events, counter_attributes, rules, intervals) :
    attributes_text = '\n\t'.join(attributes)
    events_text = '\n'.join(events)
    counter_attributes_text = '\n\t'.join(counter_attributes)
    rules_text = '\n'.join(rules)
    interval_text = '\n'.join(intervals)
    file = open('knowledge_field_template.txt', 'r', encoding='utf-8')
    template = file.read()
    file.close()
    text = template.replace('attributes', attributes_text)
    text = text.replace('classes', counter_attributes_text)
    text = text.replace('intervals', interval_text)
    text = text.replace('events', events_text)
    text = text.replace('rules', rules_text)
    return text

def knowledge_field(df, aliases, classes, time_name, clf, n) :
    feature_names = list(filter(lambda x: x != classes and x != time_name, list(df)))
    times = sorted(list(set(df[time_name].to_list())))
    class_names_aliases = list(set(df[classes].to_list()))
    class_names = list(map(lambda x: aliases.get(classes).get(int(x)), class_names_aliases))
    attributes = list(map(lambda x: get_attribute(x), feature_names))
    events = list(map(lambda x: get_event(x), times))
    counter_attributes = list(map(lambda x: get_attribute(x), class_names))
    rules = []
    intervals = []
    for i in range(n) :
        interval, rule = parse_tree(str(clf.estimators[i].visualize_tree()),
                        feature_names, aliases, classes, times)
        rules = [*rules, *rule]
        intervals = [*intervals, *interval]
    result_rules = get_result_rules(class_names, n)
    rules = [*rules, *result_rules]
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

def get_interval(node, start_time) :
    file = open('interval_template.txt', 'r', encoding='utf-8')
    template = file.read()
    file.close()
    #intervals.get(current_node)[0][1]
    node_time = node[3]
    trashold = node[2]
    value = node[1]
    plus_start = f'Таймер.такт = {node_time} + {start_time} & ГлавныйОбъект.{value} < {trashold}'
    plus_end = f'Таймер.такт = {node_time} - 1'
    minus_start = f'Таймер.такт = {node_time} & ГлавныйОбъект.{value} >= {trashold}'
    minus_end = f'Таймер.такт = {node_time} - 1'
    rule_plus = template.replace('node_name', f'{node[0]}_plus')
    rule_plus = rule_plus.replace('start_condition', plus_start)
    rule_plus = rule_plus.replace('end_condition', plus_end)
    rule_minus = template.replace('node_name', f'{node[0]}_minus')
    rule_minus = rule_minus.replace('start_condition', minus_start)
    rule_minus = rule_minus.replace('end_condition', minus_end)
    return f'{rule_plus}\n{rule_minus}'

def get_rule(start_node, leave, unparsed_arr, start_time) :
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
    conditions = []
    nodes = list(set(list(map(lambda x: x[0], pointers))))
    interval_aliases = {}
    for node in nodes :
        aliases = list(filter(lambda x: node == x[0], pointers))
        interval_aliases.update({aliases[0][1]: 'minus', aliases[1][1]: 'plus'})
    for current_node in path[:len(path)-1] :
        interval_condition = f'Событие_{start_time} d Интервал_{current_node}_{
            interval_aliases.get(path[path.index(current_node)+1])}'
        conditions.append(interval_condition)
    condition_text = ' & '.join(conditions)
    file = open('rule_template.txt', 'r', encoding='utf-8')
    rule = file.read()
    rule = rule.replace('interval_conditions', condition_text)
    rule = rule.replace('class', leave[1])
    rule = rule.replace('name', leave[0])
    #intervals.get(current_node)[0][1]
    file.close()
    return rule

def parse_tree(string, feature_names, class_aliases, class_column, times) :
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
    intervals = []
    for node in nodes :
        for time in times :
            intervals.append(get_interval(node, time))
    rules = []
    for leave in leaves :
        for time in times :
            rules.append(get_rule(node_list[0], leave, arr, time))
    return intervals, rules