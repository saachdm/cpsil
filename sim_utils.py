import socket
import struct
import threading
import dynamic_model
import dearpygui.dearpygui as dpg
import math
import numpy as np

class SimConfig():
    def __init__(self,UDP_IP,UDP_PORT,TIMESTEP):
        self.UDP_IP = UDP_IP 
        self.UDP_PORT = UDP_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timestep = TIMESTEP  # second
        self.simrun = False
        self.sim_thread = None  # Thread variable
        self.time=0
        
        # Sim constants and initial value
        self.v0 = 4
        self.vref=5
        # Sim variables
        self.v_arr=[]
        self.time_arr=[] 
        self.v_ref_arr=[]
        self.u1_arr=[]
        self.u2_arr=[]
        self.u3_arr=[]
        self.Fzf_arr=[]
        self.Fzr_arr=[]
        self.T_arr=[]
        self.omega_arr=[]
        
        # Dynamic model
        self.dyn_mod = dynamic_model.dynMod_simpletwowheelLong_wgear(self.v0, self.timestep)
        
        print("Sim object initialized")
        
    def sim_pause(self):
        self.simrun = False
        
    def sim_start(self):
        if not self.simrun:
            self.simrun = True
            self.sim_thread = threading.Thread(target=self.sim_loop)
            self.sim_thread.start()
                   
    def set_vref(self, sender, data):
        self.vref = data
    
    def set_inclination(self,sender,data):
        self.dyn_mod.incline=np.deg2rad(data)
    
    ## Move to dynamic model
    # def change_gear(self,sender,data):
    #     print(sender)
    #     if sender=="gearup" and self.dyn_mod.gear<4 :
    #         self.dyn_mod.gear+=1
    #     elif sender=="geardown" and self.dyn_mod.gear>0:
    #         self.dyn_mod.gear-=1
    #     else:
    #         None
    
    def change_gear(self,sender,data):
        if sender=="gearup":
            self.dyn_mod.change_gear(1) #1--> Up; 2--> Down
        elif sender=="geardown":
            self.dyn_mod.change_gear(2)
        else:
            None

    def set_arrays(self):
        max_size=10000
        self.v_arr.append(self.dyn_mod.v)
        self.v_ref_arr.append(self.vref)
        self.time_arr.append(self.time)
        self.Fzf_arr.append(self.dyn_mod.Ffz)
        self.Fzr_arr.append(self.dyn_mod.Frz)
        self.T_arr.append(self.dyn_mod.eng_T)
        self.omega_arr.append(self.dyn_mod.eng_omega)

        if len(self.v_arr) > max_size: # Well, assuming self.v_arr always has the same length with the rest
            self.v_arr = self.v_arr[1:]
            self.v_ref_arr = self.v_ref_arr[1:]
            self.time_arr = self.time_arr[1:]
            self.Fzf_arr = self.Fzf_arr[1:]
            self.Fzr_arr = self.Fzr_arr[1:]
            self.T_arr = self.T_arr[1:]
            self.omega_arr = self.omega_arr[1:]


    def sim_loop(self): 

        MESSAGE = struct.pack('<ff', float(self.dyn_mod.v), self.vref)  
        self.sock.sendto(MESSAGE, (self.UDP_IP, self.UDP_PORT))

        data, server_address = self.sock.recvfrom(self.UDP_PORT)
        unpacked_data = struct.unpack('<ffi', data)
        self.dyn_mod.step(unpacked_data[0], unpacked_data[1],unpacked_data[2])
        self.u1_arr.append(unpacked_data[0])
        self.u2_arr.append(unpacked_data[1]) 
        self.u3_arr.append(unpacked_data[2])
        self.time+=self.timestep
            

class sim_visualization_data():

    def __init__(self,sim_obj):
        self.sim_obj=sim_obj
        with dpg.window(label="CPysil",tag="Controller"):
            with dpg.theme(tag="button_theme"):
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (17, 10, 114), category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (92, 92, 92), category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 120, 0), category=dpg.mvThemeCat_Core)

            dpg.add_button(label="Pause", callback=sim_obj.sim_pause,pos=(10,20),width=120,height=50)
            dpg.add_button(label="Run Simulation", callback=sim_obj.sim_start,pos=(10,100),width=120,height=50)
            dpg.add_slider_float(label="Velocity Reference", callback=sim_obj.set_vref, default_value=sim_obj.vref,
                                min_value=0.0, max_value=20.0, pos=(10, 200), width=300, height=50)
            dpg.add_slider_float(label="Road inclination", callback=sim_obj.set_inclination, default_value=sim_obj.dyn_mod.incline,
                                min_value=-4.0, max_value=4.0, pos=(10, 300), width=300, height=50)
            dpg.add_button(label="Gear +", callback=sim_obj.change_gear,pos=(10,500),width=120,height=50,tag='gearup')
            dpg.add_button(label="Gear -", callback=sim_obj.change_gear,pos=(10,550),width=120,height=50,tag='geardown')
            dpg.add_text("Simulation time: 0", tag="simulation_time_text",pos=(10,350))
            dpg.add_text("Time elapsed: 0", tag="time_elapsed_text",pos=(10,375))
            dpg.add_text("Distance driven (km): 0", tag="distance_driven_text",pos=(10,400))
            dpg.add_text("Avg fuel consumption (km/L): 0", tag="avg_consumption_text",pos=(10,425))
            dpg.add_text("Current gear: 0", tag="current_gear_text",pos=(10,450))
            dpg.add_text("Engine stall: 0", tag="is_stall_text",pos=(10,475))

            dpg.bind_item_theme("Controller", "button_theme")
            
        with dpg.window(label="CPysil",tag="Plotter",pos=(500,10)):
            data_y = [0.0] * 10000
            data_x = [0.0] * 10000

            with dpg.theme(tag="plot_theme"):
                with dpg.theme_component(dpg.mvScatterSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (60, 150, 200), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Cross, category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 7, category=dpg.mvThemeCat_Plots)
            with dpg.theme(tag="shadow_theme"):
                with dpg.theme_component(dpg.mvScatterSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (169, 169, 169), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Cross, category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 4, category=dpg.mvThemeCat_Plots)
                with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_color(dpg.mvPlotCol_Line, (169, 169, 169), category=dpg.mvThemeCat_Plots)
                        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2.0, category=dpg.mvThemeCat_Plots)


            with dpg.plot(label='Velocity (m/s)',height=250,width=500,pos=(10,10)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="Time (s)",tag="x_axis_1")
                dpg.add_plot_axis(dpg.mvYAxis,label="m/s",tag="y_axis_1")
                dpg.add_line_series(data_x,data_y, label="velocity", parent="y_axis_1", tag="v_plotline")
                dpg.add_line_series(data_x,data_y, label="velocity_ref", parent="y_axis_1", tag="vref_plotline")
                
            with dpg.plot(label='Inputs',height=250,width=500,pos=(10,250)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="Time (s)",tag="x_axis_2")
                dpg.add_plot_axis(dpg.mvYAxis,label="-",tag="y_axis_2")
                dpg.add_line_series(data_x,data_y, label="Prop input", parent="y_axis_2", tag="u1_plotline")
                dpg.add_line_series(data_x,data_y, label="Brake input", parent="y_axis_2", tag="u2_plotline")
                
            with dpg.plot(label='Vertical forces',height=250,width=500,pos=(10,500)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="Time (s)",tag="x_axis_3")
                dpg.add_plot_axis(dpg.mvYAxis,label="N",tag="y_axis_3")
                dpg.add_line_series(data_x,data_y, label="Fzf", parent="y_axis_3", tag="Fzf_plotline")
                dpg.add_line_series(data_x,data_y, label="Fzr", parent="y_axis_3", tag="Fzr_plotline")

            with dpg.plot(label='Engine operating point',height=250,width=700,pos=(10,750)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="RPM",tag="x_axis_4")
                dpg.add_plot_axis(dpg.mvYAxis,label="Torque (Nm)",tag="y_axis_4")
                dpg.add_line_series(data_x,data_y, label="T-w", parent="y_axis_4", tag="T-w_plotline")
                dpg.add_scatter_series([1],[1], label="T-w", parent="y_axis_4", tag="T-w_plotscatter")
                dpg.add_scatter_series([1],[1], label="T-w", parent="y_axis_4", tag="T-w_shadow_plotscatter")
                dpg.bind_item_theme("T-w_plotscatter", "plot_theme")
                dpg.bind_item_theme("T-w_shadow_plotscatter", "shadow_theme")
                dpg.bind_item_theme("T-w_plotline", "shadow_theme")


    def plotting_routine(self):
    
        ##Figure 1 (Velocity)
        dpg.set_value("v_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.v_arr[-10000:])])
        dpg.set_value("vref_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.v_ref_arr[-10000:])])
        max_y_value = max(max(self.sim_obj.v_arr),max(self.sim_obj.v_ref_arr))
        upper_limit = math.ceil(max_y_value)+0.05*max_y_value
        dpg.set_axis_limits("y_axis_1", 0, upper_limit)
        dpg.fit_axis_data('x_axis_1')
        
        ## Figure 2 (Inputs)
        dpg.set_value("u1_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.u1_arr[-10000:])])
        dpg.set_value("u2_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.u2_arr[-10000:])])
        dpg.set_axis_limits("y_axis_2", -0.2,1.2)
        dpg.fit_axis_data('x_axis_2')
        
        ## Figure 3 (Fz)
        dpg.set_value("Fzf_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.Fzf_arr[-10000:])])
        dpg.set_value("Fzr_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.Fzr_arr[-10000:])]) 
        max_y_value = max(max(self.sim_obj.Fzf_arr),max(self.sim_obj.Fzr_arr))
        upper_limit = math.ceil(max_y_value)+0.05*max_y_value
        dpg.set_axis_limits("y_axis_3", 0, upper_limit)
        dpg.fit_axis_data('x_axis_3')

        ## Figure 4 (T-w)
        radps2rpm= lambda radps_list: list(map(lambda rad_per_s: rad_per_s * 60 / (2 * math.pi), radps_list))
        dpg.set_value("T-w_plotscatter", [list(radps2rpm(self.sim_obj.omega_arr[-1:])),list(self.sim_obj.T_arr[-1:])])
        dpg.set_value("T-w_shadow_plotscatter", [list(radps2rpm(self.sim_obj.omega_arr[-5:-1])),list(self.sim_obj.T_arr[-5:-1])])
        dpg.set_value("T-w_plotline", [list(radps2rpm(self.sim_obj.omega_arr[-100:])),list(self.sim_obj.T_arr[-100:])]) 
        dpg.set_axis_limits("x_axis_4", -200, 8000)
        dpg.set_axis_limits("y_axis_4", -20, 220)
