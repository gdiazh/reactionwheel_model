# -*- coding: utf-8 -*-

"""
* @file dc_motor.py
* @author Gustavo Diaz H.
* @date 18 Jul 2020
* @brief Simple model of a DC Motor
"""

import numpy as np

class DCMOTOR(object):
    def __init__(self, R, L, ke, kt, kf, J, dt, delay):
        # Parameters
        self.R = R              # Motor coil resistance
        self.L = L              # Motor coil inductance
        self.ke = ke            # Motor BEMF constant
        self.kt = kt            # Motor torque constant
        self.kf = kf            # Motor friction constant
        self.J = J              # Motor's Rotor Moment of Inertia
        # State variables
        self.x = np.zeros(3)    # state x = [current, omega, theta] (3x1 vector)
        self.current = 0        # state 1. Notation: i
        self.omega = 0          # state 2. Notation: w
        self.theta = 0          # state 3. Notation: th
        self.torque_e = 0       # Electric torque, Te = kt*i
        # delayed model
        self.delay = delay
        self.kdelay = int(self.delay/dt)
        self.delayed_voltages = np.zeros(self.kdelay+1)

    def main_routine(self, V, TL, dt):
        Vdelayed = self.delayed_voltages[0]
        # print(self.delayed_voltages)
        # print(Vdelayed)
        self.rungeKutta(Vdelayed, TL, dt)
        self.current = self.x[0]
        self.omega = self.x[1]
        self.theta = self.x[2]
        self.torque_e = self.kf*self.current
        self.delayed_voltages = np.roll(self.delayed_voltages, -1)
        self.delayed_voltages[-1] = V
        # print("rolled:", self.delayed_voltages)

    def dynamics_current(self, current, omega, V):
        di_dt = -(self.R/self.L)*current - (self.ke/self.L)*omega + (1/self.L) * V
        return di_dt

    def dynamics_omega(self, current, omega, TL):
        dw_dt = (self.kt/self.J)*current - (self.kf/self.J)*omega - (1/self.J) * TL
        return dw_dt

    def dynamics_theta(self, omega):
        dth_dt = omega
        return dth_dt

    def dynamics_motor(self, x, V, TL):
        i = x[0]
        w = x[1]
        th = x[2]
        di_dt = self.dynamics_current(i, w, V)
        dw_dt = self.dynamics_omega(i, w, TL)
        dth_dt = self.dynamics_theta(w)
        dx_dt = np.array([di_dt, dw_dt, dth_dt])
        return dx_dt

    def rungeKutta(self, V, TL, dt):
        """
        * Runge-Kutta method to integrate the motor's differential equation
        *
        * @param V float Actual input Voltage
        * @param TL float Actual input Load Torque
        * @param dt float integration time step
        * @update x float Next states (i, w, th)
        * @update Te float Next electric torque state
        """
        k1 = self.dynamics_motor(self.x, V, TL)
        k2 = self.dynamics_motor(self.x + 0.5*dt*k1, V, TL)
        k3 = self.dynamics_motor(self.x + 0.5*dt*k2, V, TL)
        k4 = self.dynamics_motor(self.x + dt*k3, V, TL)

        self.x = self.x + dt*(k1 + 2*(k2+k3)+k4)/6.0