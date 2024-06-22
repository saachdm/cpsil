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
v0=8
f0=0
timestep=0.01

dyn_mod=dynamic_model.dynMod_simpletwowheelLong(v0,timestep)


while i<20000:
    i+=1
    sim_time+=timestep
    print(ref.square(timestep)[i])
    MESSAGE = struct.pack('<ff',float(dyn_mod.v),float(ref.square(timestep)[i]))  
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    data,server_address=sock.recvfrom(UDP_PORT)
    
    unpacked_data=struct.unpack('<f',data)
    dyn_mod.step(unpacked_data[0],0)

    velocity_vis.append_data(sim_time,dyn_mod.v,float(ref.square(timestep)[i]))

    gui.animate(instance=velocity_vis)
    time.sleep(0.001)
    
plt.ioff()
plt.show()
sock.close()


