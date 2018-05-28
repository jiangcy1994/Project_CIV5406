from itertools import product
from functools import partial
import pickle
import pathlib
import pandas as pd

from utility.AllNothingFrankWolf import AllNothingFrankWolfModel

df_demand = pd.read_excel('data.xlsx', sheet_name='demand')

list_centroid = [1] + list(df_demand.index[df_demand[1] != 0])


def cal_money_cost(x, t_a0, c_a, ex):
    return 2 * t_a0 * (1 + 0.15 * (x / c_a) **4) + ex

net_info_dir_path = pathlib.Path('net_info')
result_dir_path = pathlib.Path('scheme2')

result_dir_path.mkdir(exist_ok=True)

with open('net_info/net_info_000000.bin','rb') as readfile:
    net_info = pickle.load(readfile)
    
df_path = pd.read_csv('scheme1/result_00000000.csv')

for i in product(range(10), repeat=3):
    result_file_path = result_dir_path / ('result_' + ''.join([*map(str, i)]) + '.csv')
    if result_file_path.exists():
        continue
    
    df_path_copy = df_path.copy()
    df_path_copy['ex'] = 0
    df_path_copy.loc[df_path['v/c'] > 1.1 ,'ex'] = i[0]
    df_path_copy.loc[df_path['v/c'].between(1,1.1),'ex'] = i[1]
    df_path_copy.loc[df_path['v/c'].between(0.9,1),'ex'] = i[2]
    
    ex_list = df_path_copy.ex
    
    cost_func_list = [partial(cal_money_cost, t_a0=row['t0'], c_a=row['ca'], ex=row['ex']) for _, row in df_path_copy.iterrows()]
    
    model = AllNothingFrankWolfModel(net_info, list_centroid, df_demand, cost_func_list)
    model.init()
    model.update()
    convergence_count = 0
    while not model.convergence_test():
        model.update()
        convergence_count += 1
        if convergence_count >= 20:
            break
    
    print('{0} complete after {1} epoch'.format(''.join([*map(str, i)]), convergence_count))
    df_path_copy['volumn'] = model.x
    df_path_copy['v/c'] = model.vc_ratio(df_path_copy.ca.values)
    df_path_copy.to_csv(str(result_file_path), index=False, encoding='utf8')
