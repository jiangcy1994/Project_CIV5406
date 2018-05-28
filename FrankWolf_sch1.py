from itertools import product
from functools import partial
import pickle
import pathlib
import pandas as pd

from utility.AllNothingFrankWolf import AllNothingFrankWolfModel

MAX_EPOCH = 20

df_demand = pd.read_excel('data.xlsx', sheet_name='demand')

list_centroid = [1] + list(df_demand.index[df_demand[1] != 0])


def cal_time_cost(x, t_a0, c_a):
    return t_a0 * (1 + 0.15 * (x / c_a) **4)


net_info_dir_path = pathlib.Path('net_info')
result_dir_path = pathlib.Path('scheme1')

result_dir_path.mkdir(exist_ok=True)


for i in product(range(3), repeat=8):
    net_info_file_path = net_info_dir_path / ('net_info_' + ''.join([*map(lambda x: str(int(bool(x))), i[:-2])]) + '.bin')
    path_info_file_path = net_info_dir_path / ('path_' + ''.join([*map(str, i)]) + '.csv')
    result_info_file_path = result_dir_path / ('result_' + ''.join([*map(str, i)]) + '.csv')
    if not path_info_file_path.exists():
        continue

    if result_info_file_path.exists():
        print('exists {0}'.format(''.join([*map(str, i)])))
        continue
        
    with net_info_file_path.open(mode='rb') as readfile:
        net_info = pickle.load(readfile)
    
    current_path = pd.read_csv(str(path_info_file_path))
    cost_func_list = [partial(cal_time_cost, t_a0=row['t0'], c_a=row['ca']) for _, row in current_path.iterrows()]

    model = AllNothingFrankWolfModel(net_info, list_centroid, df_demand, cost_func_list)
    model.init()
    model.update()
    epoch_count = 0
    while not model.convergence_test():
        model.update()
        epoch_count += 1
        if epoch_count >=MAX_EPOCH:
            break

    print('{0} completed after {1} epoch'.format(''.join([*map(str, i)]), epoch_count))
    current_path['volumn'] = model.x
    current_path['v/c'] = model.vc_ratio(current_path['ca'].values)
    current_path.to_csv(result_info_file_path, index=False, encoding='utf8')
