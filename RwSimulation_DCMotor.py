# TEST
import numpy as np
import matplotlib.pyplot as plt
import time
from InputSignals.step import Step
from InputSignals.pwm import PWM
from Sensors.current_sensor import CurrentSensor
from Models.dc_motor import DCMOTOR

# Motor Parameters
V_nom = 12.0    #[V]
N_poles = 12    #[-]
R = 1.7         #[Ohm]
L = 2.5e-3      #[H]
ke = 7e-3       #[V/Hz]
kt = 6.5e-3     #[Nm/A]
kf = 2.29e-6    #[Nm*s]
J = 2.91e-6     #[Kgm^2]
tau_e = L/R     #[s]
tau_m = J/kf    #[s]
sys_delay = 0.3 #[s]
print("Electric time constant: ", tau_e)
print("Mechanic time constant: ", tau_m)
print("System delay: ", sys_delay)

# Time parameters for simulation
tf = 5*tau_m
dt = 0.3*tau_e
N = int(tf/dt)
t = np.linspace(0, tf, N)

# Motor call
dc_motor = DCMOTOR(R, L, ke, kt, kf, J, dt, sys_delay)

# Voltage Signal parameters
#Step Response
V = V_nom           #[V]
delay = 0.2*tf      #[s]
voltage_1 = Step(0, tf, dt, 0.2*V, delay).signal
voltage_2 = Step(0, tf, dt, 0.4*V, 0.4*tf).signal
voltage_3 = Step(0, tf, dt, 0.6*V, 0.6*tf).signal
voltage_4 = Step(0, tf, dt, 0.8*V, 0.8*tf).signal
voltage = voltage_1 + voltage_2 + voltage_3 + voltage_4
# voltage = Step(0, tf, dt, 0.05*V, delay).signal
#PWM input
freq = 100          #[Hz]
duty = 30           #[%]
# voltage = PWM(0, tf, dt, V_nom, freq, duty).signal

# Motor Data Storage
i_data = np.zeros(N)
w_data = np.zeros(N)
th_data = np.zeros(N)
te_data = np.zeros(N)

# Sensors
# Electric current
i_std = 22e-5       #[A]
i_bias = 22e-6      #[A]
current_sensor = CurrentSensor(i_bias, i_std)

for i in range(0, N):
    # Process data
    dc_motor.main_routine(voltage[i], 0, dt)
    
    # Data of interest
    i_data[i] = dc_motor.current
    w_data[i] = dc_motor.omega
    th_data[i] = dc_motor.theta
    te_data[i] = dc_motor.torque_e

# Save data to csv
SAVE_DATA = False
if SAVE_DATA:
    import pandas as pd
    from pathlib import Path
    import datetime
    folder = "data/"
    Path(folder).mkdir(parents=True, exist_ok=True)
    data = {"time[s]": t, "voltage[V]": voltage, "speed[rad/s]": w_data}
    df = pd.DataFrame(data, columns=["time[s]", "voltage[V]", "speed[rad/s]"])
    test_name = "VoltageSteps"
    date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    path = Path(folder+date+test_name+".csv")
    df.to_csv(path)

# Data Visualization
from Visualization.monitor import Monitor
rad_s2rpm = 60/(2*np.pi)
rad2deg = 180/np.pi

v_mon = Monitor([t], [voltage], "Motor input voltage", "V[V]", "time[s]", sig_name = ["V"])
v_mon.plot()

i_mon = Monitor([t], [i_data], "Motor electric current", "i[A]", "time[s]", sig_name = ["i"])
i_mon.plot()

w_mon = Monitor([t], [w_data*rad_s2rpm], "Motor speed", "w[rpm]", "time[s]", sig_name = ["w"])
w_mon.plot()

# th_mon = Monitor([t], [th_data*rad2deg], "Motor position", "th[deg]", "time[s]", sig_name = ["th"])
# th_mon.plot()

# te_mon = Monitor([t], [te_data*rad2deg], "Motor electric torque", "te[Nm]", "time[s]", sig_name = ["te"])
# te_mon.plot()

v_mon.show()