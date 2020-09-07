import pandas
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("..")
from Visualization.monitor import Monitor
from DataAnalysis.tools import find_step

# read data
path = "../../DRV10987_Firmware/ros_uart_controller/data/steps1/"
file0 = "2020-08-08 12-00-13[step-60].csv"
file1 = "2020-08-08 11-38-43[step-100].csv"
file2 = "2020-08-08 11-45-52[step-200].csv"
file3 = "2020-08-08 11-55-35[step-300].csv"
file4 = "2020-08-08 11-58-59[step-400].csv"
file5 = "2020-08-08 11-59-28[step-500].csv"
file6 = "2020-08-08 11-59-50[step-511].csv"

files = [file0, file1, file2, file3, file4, file5, file6]
data = [None]*len(files)
for i in range(0, len(files)):
	data[i] = pandas.read_csv(path+files[i])

times = [None]*len(data)
speed_cmds = [None]*len(data)
speeds = [None]*len(data)
for i in range(0, len(data)):
	times[i] = data[i]['time[s]'].values
	speed_cmds[i] = data[i]['speed[cmd]'].values
	speeds[i] = data[i]['speed[RPM]'].values

# Calc Speed steady state values
ssvs = np.zeros(len(speeds))
for i in range(0, len(speeds)):
	[s_offset, s_steady, t_steady] = find_step(times[i], speeds[i], debug = True)
	ssvs[i] = np.mean(s_steady)
speeds_cmds = np.array([60, 100, 200, 300, 400, 500, 511])
steady_mon = Monitor([speeds_cmds], [ssvs], "Speed step response steady states w.r.t speed cmd", "speed[RPM]", "speed[cmd]", sig_name = ["mean_steady"])
steady_mon.plot()
steady_mon.show()

K_ini = np.divide(ssvs, speeds_cmds)
print("K_ini = ", K_ini)
K_ini_mon = Monitor([speeds_cmds], [K_ini], "Speed step steady constant K states w.r.t speed cmd", "const[RPM/cmd]", "speed[cmd]", sig_name = ["mean_steady"])
K_ini_mon.plot()
K_ini_mon.show()

dead_time = [1.80, 1.80, 1.81, 1.80, 1.8, 1.8, 1.8]
taus = [2.13, 1.77, 1.17, 1.22, 1.8, 1.72, 2.12]

dead_time_mon = Monitor([speeds_cmds], [dead_time], "Speed step dead_time values w.r.t speed cmd", "dead_time[s]", "speed[cmd]", sig_name = ["dead_time"])
dead_time_mon.plot()
dead_time_mon.show()
taus_mon = Monitor([speeds_cmds], [taus], "Speed step taus values w.r.t speed cmd", "tau[s]", "speed[cmd]", sig_name = ["tau"])
taus_mon.plot()
taus_mon.show()


# Data Visualization
rad_s2rpm = 60/(2*np.pi)
rad2deg = 180/np.pi

speed_mon = Monitor(times, speeds, "Motor speed steps", "w[RPM]", "time[s]", sig_name = ["s60", "s100", "s200", "s300", "s400", "s500", "s511"])
speed_mon.plot()
speed_mon.show()