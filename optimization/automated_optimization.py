import numpy as np
import glob
from subprocess import Popen, PIPE

path = "../../DRV10987_Firmware/ros_uart_controller/data/steps/"

speeds = np.linspace(60, 511, 512-60)

for i in range(0, len(speeds)):
	file = glob.glob(path+"*-"+str(speeds[i])+"*.csv")
	file_arg = file[0][55:] + "\n"
	speed_arg = str(speeds[i])+"\n"
	print(file_arg, speed_arg)
	p = Popen(['python3 fopdt_optimize.py'], stdin=PIPE, shell=True)
	cmd = file_arg+speed_arg
	p.communicate(input=cmd.encode())
