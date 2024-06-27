import dearpygui.dearpygui as dpg
dpg.create_context()

import socket
import struct
import threading
import dynamic_model
from simvis import sim_visualization_data
import time
import numpy as np


class sim_config():
    def __init__(self):
        self.UDP_IP = "127.0.0.1"  
        self.UDP_PORT = 5050
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timestep = 0.0005  # second
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
    
    def change_gear(self,sender,data):
        print(sender)
        if sender=="gearup" and self.dyn_mod.gear<4 :
            self.dyn_mod.gear+=1
        elif sender=="geardown" and self.dyn_mod.gear>0:
            self.dyn_mod.gear-=1
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
        i=0
        while self.simrun:
            i+=1
            MESSAGE = struct.pack('<ff', float(self.dyn_mod.v), self.vref)  
            self.sock.sendto(MESSAGE, (self.UDP_IP, self.UDP_PORT))

            data, server_address = self.sock.recvfrom(self.UDP_PORT)
            
            unpacked_data = struct.unpack('<ff', data)
            if i%500==0: # TODO: Figure out a way to precisely control simulation speed
                self.set_arrays()
                simvisdata.plotting_routine()
            self.dyn_mod.step(unpacked_data[0], unpacked_data[1])
            self.u1_arr.append(unpacked_data[0])
            self.u2_arr.append(unpacked_data[1]) 
            self.time+=self.timestep
            time.sleep(0.00001)
            


sim_obj = sim_config()
simvisdata=sim_visualization_data(sim_obj)


dpg.create_viewport(title='CPysil', width=1400, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()