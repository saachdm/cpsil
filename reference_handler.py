import numpy as np

def square(timestep):
    scale=5
    timescale=10 # timestep 
    y1=np.linspace(0,0,int(timescale/timestep))
    y2=np.linspace(scale,scale,int((timescale/4)/timestep))
    y3=np.linspace(0,0,int(timescale/timestep))
    y=np.concatenate((y1,y2,y3))
    x=np.linspace(0,len(y),int(len(y)/timestep))
    return y