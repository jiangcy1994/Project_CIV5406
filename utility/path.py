def cal_link_cost(volumn, cost_func, link):
    return cost_func[link - 1](volumn)

def cal_path_cost(volumns, cost_func, path):
    return sum(cal_link_cost(volumns[link - 1], cost_func, link) for link in path)

def all_path_cost(paths, volumns, cost_funcs):
    if not paths:
        return []
    return [*map(lambda path: cal_path_cost(volumns, cost_funcs, path), paths)]

def argmin_path_cost(paths, volumns, cost_funcs):
    if not paths:
        return -1
    apc = all_path_cost(paths, volumns, cost_funcs)
    return min(range(len(paths)), 
               key=lambda path_id: apc[path_id])
