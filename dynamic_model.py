class dynMod_pointmass():
    """
    Simplest pointmass longitudinal model. Input to the system is assumed to be a multiplier of a torque constant.
    ...

    Attributes
    ----------
     v: float
        velocity
     f: float
        "force"
     timestep : float
        simulation timestep

    Methods
    -------
    step(u):
        Receives input U. Advances the model by one timestep.
    """
    
    def __init__(self,v,timestep):
        self.v=v
        self.f=0
        self.timestep=timestep
    def step(self,u):
        max_torque=200
        rho=1.225
        A=2.5
        Cd=0.3
        m=1200
        r=0.5
        f=u*max_torque*r
        self.a=((-0.5*rho*self.v**2*A*Cd)+f)/m
        self.v=self.v+self.a*self.timestep
        
class dynMod_simpletwowheelLong():
    """
    Longitudinal simple two wheel [in progress].
    ...

    Attributes
    ----------


    Methods
    -------

    """
    
    def __init__(self,v,timestep):
        self.v=v
        self.r=0.3
        self.w=self.v/self.r
        self.A=2
        self.Cd=0.3
        self.m=1500
        self.a=0
        self.Lr=1
        self.Lf=1.2
        self.timestep=timestep
    def slip(self):
        v_tang=self.w*self.r
        if self.v==0:
            return 0
        else:
            return (v_tang-self.v)/self.v
        
    def longforce(self,Fz,C):
        return Fz*C*self.slip()       
        
    def F_traction(self,u1,u2):
        Tmax=300
        Tbrakemax=100
        return Tmax*u1-Tbrakemax*u2*2
    def F_aero(self):
        return 0.5*1.225*self.v**2*self.A*self.Cd
    def Fz(self):
        return self.m*self.a*self.Lr,self.m*self.a*self.Lf
    def F_friction(self):
        Fzr,Fzl=self.Fz()
        mu=0.05
        return Fzr*mu+Fzl*mu
    def step(self,u1,u2):
        self.a=(self.F_traction(u1,u2)-self.F_aero()-self.F_friction())/(self.m+self.m*self.Lr-self.m*self.Lf)
        self.v=self.v+self.a*self.timestep
    