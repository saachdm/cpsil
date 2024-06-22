import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class VisualizationData:
    def __init__(self,plotref=False,xlabel='X',ylabel='Y'):
        self.xs = []
        self.ys = []
        self.xr=[]
        self.yr=[]
        self.figure, self.ax = plt.subplots(figsize=(5,5))
        self.line, = self.ax.plot(self.xs, self.ys)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)
        if plotref:
            self.line1,=self.ax.plot(self.xr,self.yr,c='C1')
        
    def append_data(self, timestamp, measurement,reference=0):
        self.xs.append(timestamp)
        self.ys.append(measurement)
        self.xr.append(timestamp)
        self.yr.append(reference)


def animate(instance):
    xs = instance.xs[-1000:]  
    ys = instance.ys[-1000:]
    xr = instance.xr[-1000:]  
    yr = instance.yr[-1000:]

    instance.line.set_xdata(xs)
    instance.line.set_ydata(ys)
    instance.line1.set_xdata(xr)
    instance.line1.set_ydata(yr)

    instance.ax.relim()
    instance.ax.autoscale_view()
    instance.figure.canvas.draw()
    instance.figure.canvas.flush_events()

