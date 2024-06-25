import socket
import time
import struct
import matplotlib.pyplot as plt
import gui,dynamic_model
import reference_handler as ref

## Sim init
UDP_IP = "127.0.0.1"  
UDP_PORT = 5050
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
i=0
sim_time=0
plt.ion()
velocity_vis=gui.VisualizationData(plotref=True)

## Sim constants and initial value
v0=4
f0=0
timestep=0.0005 #second
sim_end_time=40 #second
num_stepping=sim_end_time/timestep
dyn_mod=dynamic_model.dynMod_simpletwowheelLong(v0,timestep)

input_vref=ref.square(timestep,3).astype(float)

while i<num_stepping:
    i+=1
    sim_time+=timestep
    if i<=len(input_vref):
        input=input_vref[i]
    else:
        input=5
    MESSAGE = struct.pack('<ff',float(dyn_mod.v),input)  
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    data,server_address=sock.recvfrom(UDP_PORT)
    
    unpacked_data=struct.unpack('<ff',data)
    dyn_mod.step(unpacked_data[0],unpacked_data[1])
    velocity_vis.append_data(sim_time,dyn_mod.v,input)

    if i%100==0:
        gui.animate(instance=velocity_vis)
    
plt.ioff()
plt.show()
sock.close()


