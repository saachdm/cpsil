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
        
class dynMod_simpletwowheelLong:
    """
    Longitudinal simple two wheel model.
    
    Attributes
    ----------
    v : float
        Initial velocity (m/s)
    timestep : float
        Time step for the simulation (s)
    
    Methods
    -------
    slip():
        Calculate the slip ratio.
    T_traction(u1, u2):
        Calculate the traction torque based on user input.
    F_aero():
        Calculate the aerodynamic drag force.
    F_x():
        Calculate the longitudinal force.
    Fz():
        Calculate the normal forces on front and rear wheels.
    F_friction():
        Calculate the friction force.
    step(u1, u2):
        Update the model state for one time step using RK4 integration.
    """
    
    def __init__(self, v, timestep):
        self.v = v
        self.r = 0.3
        self.w = self.v / self.r
        self.A = 1.5
        self.Cd = 0.3
        self.m = 1000
        self.a = 0  # Initial acceleration
        self.Lr = 1
        self.Lf = 1.2
        self.Cx = 60000
        self.mu = 0.8
        self.timestep = timestep
        self.h = 1
        self.I = 0.5
        self.omega = self.v / self.r
        self.slip_val = 0

    def slip(self, w, v):
        v_tang = w * self.r
        if abs(v_tang) < 1e-6:  # Avoid division by near-zero
            self.slip_val=0
            return 0
        else:
            self.slip_val=(v_tang - v) / abs(v_tang)
            return (v_tang - v) / abs(v_tang)

    def T_traction(self, u1, u2):
        Tmax = 300
        Tbrakemax = 100
        return Tmax * u1 - Tbrakemax * u2

    def F_aero(self, v):
        return 0.5 * 1.225 * v**2 * self.A * self.Cd

    def F_x(self, w, v):
        Fzr, _ = self.Fz()
        Fx = self.Cx * self.slip(w, v)
        return min(Fx, Fzr * self.mu)

    def Fz(self):
        Ffz = self.m * (9.81 * self.Lr / (self.Lr + self.Lf) - self.a * (self.h / (self.Lf + self.Lr))) - self.F_aero(self.v) * self.h / (self.Lf + self.Lr)
        Frz = self.m * (9.81 * self.Lf / (self.Lr + self.Lf) + self.a * (self.h / (self.Lf + self.Lr))) + self.F_aero(self.v) * self.h / (self.Lf + self.Lr)
        return Frz, Ffz

    def F_friction(self):
        Fzr, Fzl = self.Fz()
        mu = 0.005  # Road-tire friction coefficient
        return Fzr * mu + Fzl * mu
    
    def derivatives(self, w, v, u1, u2):
        traction = self.T_traction(u1, u2)
        Fx = self.F_x(w, v)
        F_aero = self.F_aero(v)
        F_friction = self.F_friction()
        
        alpha = (traction - Fx * self.r) / self.I
        a = (Fx - F_aero - F_friction) / self.m
        self.a=a
        
        return alpha, a

    def step(self, u1, u2):
        # Calculate RK4 intermediate values
        omega1, v1 = self.omega, self.v
        k1_omega, k1_v = self.derivatives(omega1, v1, u1, u2)
        
        omega2 = omega1 + 0.5 * self.timestep * k1_omega
        v2 = v1 + 0.5 * self.timestep * k1_v
        k2_omega, k2_v = self.derivatives(omega2, v2, u1, u2)
        
        omega3 = omega1 + 0.5 * self.timestep * k2_omega
        v3 = v1 + 0.5 * self.timestep * k2_v
        k3_omega, k3_v = self.derivatives(omega3, v3, u1, u2)
        
        omega4 = omega1 + self.timestep * k3_omega
        v4 = v1 + self.timestep * k3_v
        k4_omega, k4_v = self.derivatives(omega4, v4, u1, u2)
        
        # Update states
        self.omega += (self.timestep / 6) * (k1_omega + 2 * k2_omega + 2 * k3_omega + k4_omega)
        self.v += (self.timestep / 6) * (k1_v + 2 * k2_v + 2 * k3_v + k4_v)
        
        # Update other dependent variables
        self.w = self.omega

