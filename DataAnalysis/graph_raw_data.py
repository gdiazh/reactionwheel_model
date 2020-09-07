import glob
import pandas
import numpy as np
import sys
sys.path.append("..")
from Visualization.monitor import Monitor
from tools import get_step_parameters

# read data
path = "../../DRV10987_Firmware/ros_uart_controller/data/steps/"
files = glob.glob(path+"*.csv")
cmd_range = input("Range? [cmd_low, cmd_speed]: ")
cmd_range = cmd_range.split(",")
cmd_low = int(cmd_range[0])
cmd_high = int(cmd_range[1])
# data = [None]*(cmd_high - cmd_low + 1)
data = []
cmd_readed = []
for i in range(0, len(files)):
	cmd_ = float(files[i][len(path)+24:-5])
	if cmd_low<=cmd_<=cmd_high:
		data.append(pandas.read_csv(files[i]))
		cmd_readed.append(cmd_)

times = [None]*len(data)
speed_cmds = [None]*len(data)
speeds = [None]*len(data)
for i in range(0, len(data)):
	times[i] = data[i]['time[s]'].values
	speed_cmds[i] = data[i]['speed[cmd]'].values
	speeds[i] = data[i]['speed[RPM]'].values

# Order Data
cmd_speed = [None]*len(speeds)
for i in range(0, len(speeds)):
	cmd_speed[i] = [cmd_readed[i], speeds[i], times[i]]

cmd_speed.sort()
cmd_speed = np.array(cmd_speed)
cmds_ordered = cmd_speed[:, 0]
speeds_ordered = cmd_speed[:, 1]
times_ordered = cmd_speed[:, 2]
cmd_names = ["s"+str(cmd) for cmd in cmds_ordered]

# Graph data
speed_mon = Monitor(times_ordered, speeds_ordered, "Motor speed steps", "w[RPM]", "time[s]", sig_name = cmd_names)
speed_mon.plot()
speed_mon.show()