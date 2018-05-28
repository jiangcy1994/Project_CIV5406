import copy
from itertools import product
import pickle
import pathlib
import pandas as pd

from utility.graph import all_path


MininumPath = 10
LargestDepth = 24
file_name = 'data.xlsx'
sheet_names = ['demand', 'new', -1]
total_construction_cost = 1e10
remove_t0 = 1e8

df_demand, df_new, df_path = [pd.read_excel(file_name, sheet_name=sheet_name).dropna(axis=1) for sheet_name in sheet_names]

link_buff_size = df_path.shape[0]
list_centroid = [1] + list(df_demand.index[df_demand[1] != 0])
current_path = df_path.loc[:75]

id2candidate = lambda x: x - 1
candidate2id = lambda x: x + 1

candidate_set_size = len(set(df_new.index))
construct_candidate_set_size = len(set(df_new.index)) - 2
candidate_set_list = []

for i in range(candidate_set_size):
    df_part = df_new.loc[df_new.index == candidate2id(i)]
    candidate_set_list.append(df_part)


def strip_node(net):
    for i in range(len(net)):
        for j in range(len(net[i])):
            for k in range(len(net[i][j])):
                net[i][j][k] = net[i][j][k][1::2]

net_info_dir = pathlib.Path('net_info')
net_info_dir.mkdir(exist_ok=True)

for i in product(range(2), repeat=construct_candidate_set_size):
    df_path_copy = df_path.copy()
    
    for j in range(construct_candidate_set_size):
        candidate_set = candidate_set_list[j]
        SN_ = set(candidate_set.SN).pop()
        EN_ = set(candidate_set.EN).pop()
        candidate_filter = (df_path.SN == SN_) & (df_path.EN == EN_)
        df_path_copy.loc[candidate_filter, 't0'] = list(candidate_set.ta_0)[i[j]]
    
    current_path = df_path_copy[df_path_copy.t0 != 100000000.0]
        
    gen_link_info = lambda cp: ((row[0],row[1]) for _, row in current_path.loc[current_path.SN==cp, ['Link', 'EN']].iterrows())
    net_info = [[all_path(sp, ep,LinkGen=gen_link_info,MininumPath=MininumPath, LargestDepth=LargestDepth) for ep in list_centroid] for sp in list_centroid]
    strip_node(net_info)
    
    i_str = ''
    for j in range(construct_candidate_set_size):
        i_str += str(i[j])
    
    with open('net_info/net_info_' + i_str + '.bin', 'wb') as writefile:   
        pickle.dump(net_info, writefile)


for i in product(range(3), repeat=candidate_set_size):
    df_path_copy = df_path.copy()
    cost = 0
    
    for j in range(candidate_set_size):
        candidate_set = candidate_set_list[j]
        SN_ = set(candidate_set.SN).pop()
        EN_ = set(candidate_set.EN).pop()
        candidate_filter = (df_path.SN == SN_) & (df_path.EN == EN_)
        df_path_copy.loc[candidate_filter, 'ca'] = list(candidate_set.ca)[i[j]]
        df_path_copy.loc[candidate_filter, 't0'] = list(candidate_set.ta_0)[i[j]]
        cost += list(candidate_set['construction cost'])[i[j]]
    
    if cost > total_construction_cost:
        continue
        
    i_str = ''
    for j in range(candidate_set_size):
        i_str += str(i[j])
           
    df_path_copy.to_csv('net_info/path_' + i_str + '.csv', index=False, encoding='utf8')

