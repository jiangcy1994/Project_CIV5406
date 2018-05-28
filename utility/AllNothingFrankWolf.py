from functools import partial
from itertools import product

import numpy as np
from scipy.optimize import fsolve

from utility.path import all_path_cost, argmin_path_cost

class AllNothingFrankWolfModel:
    
    alpha = 0
    
    def __init__(self, net_topo_info, centroids, demand_matrix, cost_func_list):
        self.net_topo_info = net_topo_info
        self.centroids = centroids
        self.demand_matrix = demand_matrix
        
        self.cost_func_list = cost_func_list
        self.x = np.zeros_like(cost_func_list)
        self.x_prev = np.zeros_like(cost_func_list)
    
    def alln_ass(self):
        new_x = np.zeros_like(self.x)
        for sp, ep in product(self.centroids, repeat=2):
            demand = self.demand_matrix[sp][ep]
            if demand:
                paths = self.net_topo_info[self.centroids.index(sp)][self.centroids.index(ep)]
                min_id = argmin_path_cost(paths, self.x, self.cost_func_list)
                for link in paths[min_id]:
                    new_x[link - 1] += demand
        return new_x
    
    def total_cost(self, volumns):
        num = 0
        for sp, ep in product(self.centroids, repeat=2):
            if self.demand_matrix[sp][ep]:
                paths = self.net_topo_info[self.centroids.index(sp)][self.centroids.index(ep)]
                min_cost = min(all_path_cost(paths, volumns, self.cost_func_list))
                num+= min_cost
        return num
    
    def init(self):
        self.x = self.alln_ass()
        
    def update(self):
        y = self.alln_ass()
                
        total_cost_func = lambda alpha: sum(cost_func_(x_ + alpha * (y_ - x_)) * (y_ - x_) for x_, y_, cost_func_ in zip(self.x, y, self.cost_func_list))
        alpha_solution = fsolve(total_cost_func, 0.5)[0]
        if alpha_solution < 0:
            self.alpha = 0
        elif alpha_solution > 1:
            self.alpha = 1
        else:
            self.alpha = alpha_solution
        
        self.x_prev = np.copy(self.x)
        self.x = self.x + self.alpha * (y - self.x)
    
    def convergence_test(self, threshold=1e-5):
        if self.alpha == 1:
            return False

        old_cost = self.total_cost(self.x_prev)
        new_cost = self.total_cost(self.x)

        print(new_cost, old_cost, self.alpha)
        return abs(new_cost - old_cost)/ old_cost  < threshold
    
    def vc_ratio(self, c_as):
        return self.x / c_as