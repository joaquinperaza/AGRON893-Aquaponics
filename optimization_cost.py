from scipy.optimize import Bounds
from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Optimization:

    def __init__(self, aeroponic_model):
        self.aeroponic_model = aeroponic_model
        self.aeroponic_model.calibrate(plot=False)
        self.light_bounds = [(1, 22)]
        self.water_flow_bounds = [(0.5, 2.5)]
        self.water_times_bounds = [(0, 60)]
        self.light_cost_per_day = 0.5
        self.water_cost_per_litre = 0.1
        self.motor_kwh = 0.1
        self.pwr_cost_per_kwh = 0.1
        self.price_per_kg = 1.0


    def set_motor_kwh(self, motor_kwh):
        self.motor_kwh = motor_kwh

    def set_light_cost_per_day(self, light_cost_per_day):
        self.light_cost_per_day = light_cost_per_day

    def set_water_cost_per_litre(self, water_cost_per_litre):
        self.water_cost_per_litre = water_cost_per_litre

    def set_pwr_cost_per_kwh(self, pwr_cost_per_kwh):
        self.pwr_cost_per_kwh = pwr_cost_per_kwh

    def set_price_per_kg(self, price_per_kg):
        self.price_per_kg = price_per_kg

    def simulate(self, light, water_times, water_flow):
        _, _, biomass = self.aeroponic_model.simulate_growing_season(light=light, water_times=water_times, water_flow=water_flow, plot=False)
        return biomass

    def calculate_light_cost(self, light):
        return np.sum(light * self.light_cost_per_day)

    def calculate_water_cost(self, water_flow):
        return np.sum(water_flow * 24 * self.water_cost_per_litre)

    def calculate_motor_cost(self, water_times):
        motor_working_time = np.sum(5/(water_times+5))/60
        return np.sum(motor_working_time * self.motor_kwh * self.pwr_cost_per_kwh)

    def cost(self, x):
        #split one d array into 3 arrays of equal size
        sz = x.size//3
        light = x[:sz]
        water_times = x[sz:2*sz]
        water_flow = x[2*sz:]
        yield_kg = self.simulate(light, water_times, water_flow)
        cost = self.calculate_light_cost(light) +\
               self.calculate_water_cost(water_flow) +\
               self.calculate_motor_cost(water_times) - yield_kg[-1] * self.price_per_kg
        return cost

    def optimize(self, days, light_cost=None, water_cost=None, motor_kwh=None, price_per_kg=None, pwr_cost_per_kwh=None):
        if light_cost is not None:
            self.set_light_cost_per_day(light_cost)
        if water_cost is not None:
            self.set_water_cost_per_litre(water_cost)
        if motor_kwh is not None:
            self.set_motor_kwh(motor_kwh)
        if price_per_kg is not None:
            self.set_price_per_kg(price_per_kg)
        if pwr_cost_per_kwh is not None:
            self.set_pwr_cost_per_kwh(pwr_cost_per_kwh)
        x0 = np.ones(3*days)
        res = minimize(self.cost, x0, method='SLSQP', bounds=[*self.light_bounds*days, *self.water_times_bounds*days, *self.water_flow_bounds*days])
        print(res.x)
        return res

if __name__ == "__main__":
    from aeroponic_model import AeroponicModel
    model = AeroponicModel()
    opt = Optimization(model)
    print(opt.optimize(30, light_cost=0.02, water_cost=0.01, motor_kwh=0.07, price_per_kg=100.0, pwr_cost_per_kwh=0.001))