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
# Fz_vis=gui.VisualizationData()

## Sim constants and initial value
v0=1
f0=0
timestep=0.001

dyn_mod=dynamic_model.dynMod_simpletwowheelLong(v0,timestep)


while i<20000:
    i+=1
    sim_time+=timestep
    MESSAGE = struct.pack('<ff',float(dyn_mod.v),float(ref.square(timestep,10)[i]))  
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    data,server_address=sock.recvfrom(UDP_PORT)
    
    unpacked_data=struct.unpack('<f',data)
    dyn_mod.step(unpacked_data[0],0)

    velocity_vis.append_data(sim_time,dyn_mod.v,float(ref.square(timestep,10)[i]))

    if i%10==0:
        gui.animate(instance=velocity_vis)
    # time.sleep(0.0000001)
    
plt.ioff()
plt.show()
sock.close()


