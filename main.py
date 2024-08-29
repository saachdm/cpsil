import dearpygui.dearpygui as dpg
dpg.create_context()

from sim_utils import sim_visualization_data
from sim_utils import SimConfig
import time
import numpy as np
import math


simObj = SimConfig("127.0.0.1",5050,0.0005)
simvisdata=sim_visualization_data(simObj)


dpg.create_viewport(title='CPysil', width=1400, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
i=0
dpg.set_viewport_vsync(False)
rate_limiter=1
time_since_rate_limited=0
start_time = time.time()
simulation_time=0
evaluate_frame=0
gamma_desired=1




while dpg.is_dearpygui_running():
    i+=1
    simObj.sim_loop()

    if (dpg.get_frame_count()-evaluate_frame)%rate_limiter==0:
        simObj.set_arrays()
        simvisdata.plotting_routine()
        

    tau_sim=0.0005
    tau_real=dpg.get_delta_time()
    if math.isclose(0.0,tau_real):
        tau_real=0.00001
    gamma=tau_sim/tau_real
    try:
        simulation_time=simObj.time_arr[-1]
    except:
        simulaton_time=0
    elapsed_time=time.time()-start_time
    simulation_elapsed_diff=(simulation_time-elapsed_time)
    # print("gamma: ",gamma)
    if dpg.get_frame_count()%100==0:
        #Time to evaluate
        evaluate_frame=dpg.get_frame_count()
    if gamma>gamma_desired:
        time.sleep(tau_sim-tau_real)
        time_since_rate_limited=0 #reset limiter counter
        rate_limiter-=5
    else:
        rate_limiter+=10
        time_since_rate_limited+=1
    rate_limiter=max(1,rate_limiter)
    rate_limiter=min(rate_limiter,100)
    if dpg.get_frame_count()%1000==0:
        dpg.set_value("simulation_time_text", f"Simulation time: {simulation_time:.2f}")
        dpg.set_value("time_elapsed_text", f"Time elapsed: {elapsed_time:.2f}")
        dpg.set_value("distance_driven_text", f"Distance driven (km): {(simObj.dyn_mod.distance_driven)/1000:.2f}")
        dpg.set_value("avg_consumption_text", f"Fuel consumption (km/L): {(simObj.dyn_mod.distance_driven/1000)/simObj.dyn_mod.fuel_consumption:.4f}")
        dpg.set_value("current_gear_text", f"Current gear: {(simObj.dyn_mod.gear+1):.0f}")
        dpg.set_value("is_stall_text", f"Engine stall: {(simObj.dyn_mod.isStall)}")


    # print("Rate limiter: ",evaluate_frame+rate_limiter)
    print(simObj.dyn_mod.fuel_consumption)
    dpg.render_dearpygui_frame()

dpg.destroy_context()