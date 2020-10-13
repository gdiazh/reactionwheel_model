# -*- coding: utf-8 -*-

"""
* @file dc_motor.py
* @author Gustavo Diaz H.
* @date 29 Sep 2020
* @brief First order plus dead time model of a BLDC Motor based on experimental data
"""

import numpy as np

# Operation Zones
W0 = 61
W1 = 200
W2 = 300
W3 = 511
# Constants
rpm2rad_s = (np.pi)/30

class FOPDTMOTOR(object):
    def __init__(self, J, dt):
        # Parameters
        self.m_k = [-0.0121, -0.0252, -0.0342]      # static gain LSR-m params by region [RPM/cmd2]
        self.b_k = [25.04, 26.84, 29.87]            # static gain LSR-b params by region [RPM/cmd]
        self.m_tau = [-0.0049, 0.0003, 0.0005]      # time constant LSR-m params by region [s/cmd]
        self.b_tau = [3.95-3.0, 2.74-2.7, 2.86-2.8] # time constant LSR-b params by region [s]
        self.region = 0                             # operation region
        self.k = self.m_k[0]*0+self.b_k[0]          # Model static gain [RPM/cmd]
        self.tau = self.m_tau[0]*0+self.b_tau[0]    # Model time constant [s]
        self.deadtime = 1.81                        # Model dead time [s]
        self.J = J                                  # Motor's Rotor Moment of Inertia
        # State variables
        self.x = np.zeros(2)    # state x = [omega, theta] (3x1 vector)
        self.omega = 0          # state 1. Notation: w
        self.theta = 0          # state 2. Notation: th
        self.alpha = 0          # Angular acceleration, alpha = (w(k)-w(k-1))/ dt
        self.torque_e = 0       # Electric torque, Te = kt*i
        # delayed variables
        self.kdelay = int(self.deadtime/dt)
        self.delayed_omegaRef = np.zeros(self.kdelay+1)

    def main_routine(self, OMEGAREF, TL, dt):
        wRdelayed = self.delayed_omegaRef[0]
        # print(self.delayed_omegaRef)
        # print(wRdelayed)
        self.rungeKutta(wRdelayed, TL, dt)
        self.alpha = (self.x[0]-self.omega)/dt
        self.omega = self.x[0]
        self.theta = self.x[1]
        self.torque_e = self.J*self.alpha
        self.delayed_omegaRef = np.roll(self.delayed_omegaRef, -1)
        self.delayed_omegaRef[-1] = OMEGAREF
        # print("rolled:", self.delayed_omegaRef)

    def dynamics_omega(self, omega, OMEGAREF):
        # check operation zone
        if 0<OMEGAREF<=W0:
            self.region = 0
        elif W0<OMEGAREF<=W1:
            self.region = 1
        elif W1<OMEGAREF<=W2:
            self.region = 2
        elif W2<OMEGAREF<=W3:
            self.region = 3
        # set parameters according to operation zone
        if self.region == 0:
            dw_dt = 0
        else:
            self.k = self.m_k[self.region-1]*OMEGAREF + self.b_k[self.region-1]
            dw_dt = (self.k*OMEGAREF*rpm2rad_s - omega)/self.tau
        
        return dw_dt

    def dynamics_theta(self, omega):
        dth_dt = omega
        return dth_dt

    def dynamics_motor(self, x, OMEGAREF):
        w = x[0]
        th = x[1]
        dw_dt = self.dynamics_omega(w, OMEGAREF)
        dth_dt = self.dynamics_theta(w)
        dx_dt = np.array([dw_dt, dth_dt])
        return dx_dt

    def rungeKutta(self, OMEGAREF, TL, dt):
        """
        * Runge-Kutta method to integrate the motor's differential equation
        *
        * @param OMEGAREF float Actual input angular rate reference
        * @param dt float integration time step
        * @update x float Next states (i, w, th)
        """
        k1 = self.dynamics_motor(self.x, OMEGAREF)
        k2 = self.dynamics_motor(self.x + 0.5*dt*k1, OMEGAREF)
        k3 = self.dynamics_motor(self.x + 0.5*dt*k2, OMEGAREF)
        k4 = self.dynamics_motor(self.x + dt*k3, OMEGAREF)

        self.x = self.x + dt*(k1 + 2*(k2+k3)+k4)/6.0