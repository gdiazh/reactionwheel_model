# TEST
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas
from InputSignals.step import Step
from InputSignals.pwm import PWM
from Models.fopdt_model import FOPDTMOTOR

# Motor Parameters
J = 2.91e-6     #[Kgm^2]
tau_m = 1       #[s]
print("System time constant: ", tau_m)

# Time parameters for simulation
tf = 50
dt = 0.3*tau_m
N = int(tf/dt)
t = np.linspace(0, tf, N)

# Motor call
fopdt_motor = FOPDTMOTOR(J, dt)

# speed Signal parameters
#Step Response
delay = 0.2*tf      #[s]
speed_1 = Step(0, tf, dt, 123, 0).signal
speed_2 = Step(0, tf, dt, 111, 10).signal
speed_3 = Step(0, tf, dt, 53, 20).signal
speed_4 = Step(0, tf, dt, -105, 30).signal
speed_5 = Step(0, tf, dt, -182, 40).signal
speed = speed_1 + speed_2 + speed_3 + speed_4 + speed_5
# speed = Step(0, tf, dt, 0.05*V, delay).signal
#PWM input
freq = 100          #[Hz]
duty = 30           #[%]
# speed = PWM(0, tf, dt, V_nom, freq, duty).signal

# Motor Data Storage
w_data = np.zeros(N)
th_data = np.zeros(N)
te_data = np.zeros(N)

# run simulation
for i in range(0, N):
    # Process data
    fopdt_motor.main_routine(speed[i], 0, dt)
    
    # Data of interest
    w_data[i] = fopdt_motor.omega
    th_data[i] = fopdt_motor.theta
    te_data[i] = fopdt_motor.torque_e

# Save data to csv
SAVE_DATA = False
if SAVE_DATA:
    import pandas as pd
    from pathlib import Path
    import datetime
    folder = "data/"
    Path(folder).mkdir(parents=True, exist_ok=True)
    data = {"time[s]": t, "speed[V]": speed, "speed[rad/s]": w_data}
    df = pd.DataFrame(data, columns=["time[s]", "speed[V]", "speed[rad/s]"])
    test_name = "speedSteps"
    date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    path = Path(folder+date+test_name+".csv")
    df.to_csv(path)

# read data
path = "../DRV10987_Firmware/ros_uart_controller/data/signalm1/"
name = "2020-10-12 20-39-44[model_signal]"
file = path+name+".csv"
data = pandas.read_csv(file)

time_data = data['time[s]'].values
speedcmd_data = data['speed[cmd]'].values
speed_data = data['speed[RPM]'].values

# remove align time overflow
for i in range(0, len(speed_data)):
    if speed_data[i]>8000:
        speed_data[i] = 0

# Data Visualization
from Visualization.monitor import Monitor
rad_s2rpm = 60/(2*np.pi)
rad2deg = 180/np.pi

v_mon = Monitor([t, time_data], [speed, speedcmd_data], "Motor input speed", "speed[cmd]", "time[s]", sig_name = ["model_cmd", "data_cmd"])
v_mon.plot()

w_mon = Monitor([t, time_data], [w_data*rad_s2rpm, speed_data], "Motor speed", "w[rpm]", "time[s]", sig_name = ["model_w", "data_w"])
w_mon.plot()

# th_mon = Monitor([t], [th_data*rad2deg], "Motor position", "th[deg]", "time[s]", sig_name = ["th"])
# th_mon.plot()

# te_mon = Monitor([t], [te_data], "Motor electric torque", "te[Nm]", "time[s]", sig_name = ["te"])
# te_mon.plot()

v_mon.show()