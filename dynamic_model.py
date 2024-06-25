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
    Longitudinal simple two-wheel model with rear-wheel drive and brakes on both wheels.

    Attributes
    ----------
    v : float
        Initial velocity (m/s)
    timestep : float
        Simulation timestep (s)
    
    Methods
    -------
    slip(w, v):
        Calculate the slip ratio.
    T_traction(u1):
        Calculate the traction torque based on user input.
    T_brake_front(u2):
        Calculate the braking torque for the front wheel based on user input.
    T_brake_rear(u2):
        Calculate the braking torque for the rear wheel based on user input.
    F_aero(v):
        Calculate the aerodynamic drag force.
    F_x(w, v, Fz):
        Calculate the longitudinal force based on slip and normal force.
    Fz():
        Calculate the normal forces on front and rear wheels.
    F_friction(Fzr, Fzf):
        Calculate the friction force based on normal forces.
    derivatives(wr, wf, v, u1, u2):
        Calculate derivatives for integration.
    step(u1, u2):
        Update the model state for one time step using RK4 integration.
    """
    
    def __init__(self, v, timestep):
        self.v = v  # Initial velocity
        self.r = 0.3  # Wheel radius (m)
        self.A = 1.5  # Frontal area (m^2)
        self.Cd = 0.3  # Drag coefficient
        self.m = 1000  # Mass (kg)
        self.a = 0  # Initial acceleration
        self.Lr = 1  # Distance from CG to rear axle (m)
        self.Lf = 1.2  # Distance from CG to front axle (m)
        self.Cx = 30000  # Longitudinal tire stiffness for both front and rear(N)
        self.mu = 0.8  # Friction coefficient
        self.timestep = timestep  # Time step (s)
        self.h = 1  # Height of CG (m)
        self.Ir = 0.5  # Rear wheel inertia (kg.m^2)
        self.If = 0.5  # Front wheel inertia (kg.m^2)
        self.omega_r = self.v / self.r  # Initial rear wheel angular velocity (rad/s)
        self.omega_f = self.v / self.r  # Initial front wheel angular velocity (rad/s)
        self.slip_r = self.slip(self.omega_r, self.v)  # Rear wheel slip ratio
        self.slip_f = self.slip(self.omega_f, self.v)  # Front wheel slip ratio
        Frz_init,Ffz_init=self.Fz()
        self.Frz = Frz_init  # Rear normal force
        self.Ffz = Ffz_init  # Front normal force
        self.brake_dist = 0.6  # Braking distribution ratio (front/rear)

    def slip(self, w, v):
        v_tang = w * self.r
        if abs(v_tang) < 1e-6:  # Avoid division by near-zero
            return 0
        return (v_tang - v) / abs(v_tang)

    def T_traction(self, u1): #Assuming only one wheel is propelled (rear)
        Tmax = 100  # Max propulsive torque
        u1=min(u1,1) #Saturate U1 to be always below 1
        propulsive_U = max(0, u1)  # Saturate to enable coasting (T=0) when U input is <0
        return Tmax * propulsive_U

    def T_brake_front(self, u2):
        Tbrakemax = 75  # Max braking torque
        u2=min(u2,1) #Saturate U2 to be always below 1
        braking_U = max(0, u2)  # Saturate to prevent "negative braking"
        return Tbrakemax * braking_U * self.brake_dist

    def T_brake_rear(self, u2):
        Tbrakemax = 75  # Max braking torque
        u2=min(u2,1) #Saturate U2 to be always below 1
        braking_U = max(0, u2)  # Saturate to prevent "negative braking"
        return Tbrakemax * braking_U * (1 - self.brake_dist)

    def F_aero(self, v):
        return 0.5 * 1.225 * v**2 * self.A * self.Cd

    def F_x(self, w, v, Fz):
        Fx = self.Cx * self.slip(w, v)
        return min(Fx, Fz * self.mu)

    def Fz(self):
        # Calculate normal forces
        Ffz = self.m * (9.81 * self.Lr / (self.Lr + self.Lf) - self.a * (self.h / (self.Lf + self.Lr))) - self.F_aero(self.v) * self.h / (self.Lf + self.Lr)
        Frz = self.m * (9.81 * self.Lf / (self.Lr + self.Lf) + self.a * (self.h / (self.Lf + self.Lr))) + self.F_aero(self.v) * self.h / (self.Lf + self.Lr)
        return Frz, Ffz

    def F_friction(self, Fzr, Fzf):
        if self.v == 0:
            mu = 0
        else:
            mu = 0.005  # Rolling friction coefficient
        return Fzr * mu + Fzf * mu

    def derivatives(self, wr, wf, v, u1, u2):
        self.Frz, self.Ffz = self.Fz()
        traction = self.T_traction(u1)
        braking_front = self.T_brake_front(u2)
        braking_rear = self.T_brake_rear(u2)
        Fx_r = self.F_x(wr, v, self.Frz) 
        Fx_f = self.F_x(wf, v, self.Ffz)
        F_aero = self.F_aero(v)
        F_friction = self.F_friction(self.Frz, self.Ffz)
        
        alpha_r = (traction - braking_front - Fx_r * self.r) / self.Ir
        alpha_f = (-braking_rear -Fx_f * self.r) / self.If
        a = (Fx_r + Fx_f - F_aero - F_friction - braking_front*self.r - braking_rear*self.r) / self.m
        self.a = a
        
        return alpha_r, alpha_f, a

    def step(self, u1, u2):
        """
        Update the model state for one time step using RK4 integration.
        
        Parameters
        ----------
        u1 : float
            User input for traction control.
        u2 : float
            User input for braking control.
        """
        h = self.timestep
        # Initial state
        omega_r1, omega_f1, v1 = self.omega_r, self.omega_f, self.v

        # RK4 intermediate steps
        k1_omega_r, k1_omega_f, k1_v = self.derivatives(omega_r1, omega_f1, v1, u1, u2)

        omega_r2 = omega_r1 + 0.5 * h * k1_omega_r
        omega_f2 = omega_f1 + 0.5 * h * k1_omega_f
        v2 = v1 + 0.5 * h * k1_v
        k2_omega_r, k2_omega_f, k2_v = self.derivatives(omega_r2, omega_f2, v2, u1, u2)

        omega_r3 = omega_r1 + 0.5 * h * k2_omega_r
        omega_f3 = omega_f1 + 0.5 * h * k2_omega_f
        v3 = v1 + 0.5 * h * k2_v
        k3_omega_r, k3_omega_f, k3_v = self.derivatives(omega_r3, omega_f3, v3, u1, u2)

        omega_r4 = omega_r1 + h * k3_omega_r
        omega_f4 = omega_f1 + h * k3_omega_f
        v4 = v1 + h * k3_v
        k4_omega_r, k4_omega_f, k4_v = self.derivatives(omega_r4, omega_f4, v4, u1, u2)

        # Update states
        self.omega_r += (h / 6) * (k1_omega_r + 2 * k2_omega_r + 2 * k3_omega_r + k4_omega_r)
        self.omega_f += (h / 6) * (k1_omega_f + 2 * k2_omega_f + 2 * k3_omega_f + k4_omega_f)
        self.v += (h / 6) * (k1_v + 2 * k2_v + 2 * k3_v + k4_v)
        self.slip_r = self.slip(self.omega_r, self.v)
        self.slip_f = self.slip(self.omega_f, self.v)
