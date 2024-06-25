import numpy as np

def square(timestep,length):
    #Length in seconds
    scale=5
    square_time=length/timestep 
    baseline=2
    y1=np.linspace(baseline,baseline,int(square_time/5))
    y2=np.linspace(scale,scale,int(square_time))
    y3=np.linspace(baseline,baseline,int(square_time/2))
    y=np.concatenate((y1,y2,y3))
    return y