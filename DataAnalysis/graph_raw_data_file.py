import glob
import pandas
import numpy as np
import sys
sys.path.append("..")
from Visualization.monitor import Monitor

# read data
path = "../../DRV10987_Firmware/ros_uart_controller/data/inisteps/"
name = "2020-10-13 21-51-51[511]"
file = path+name+".csv"
data = pandas.read_csv(file)

time = data['time[s]'].values
speed_cmd = data['speed[cmd]'].values
speed = data['speed[RPM]'].values

# Graph data
cmd_mon = Monitor([time], [speed_cmd], "Motor speed cmd", "w[cmd]", "time[s]", sig_name = ["cmd"])
cmd_mon.plot()

speed_mon = Monitor([time], [speed], "Motor speed", "w[RPM]", "time[s]", sig_name = ["speed"])
speed_mon.plot()
speed_mon.show()