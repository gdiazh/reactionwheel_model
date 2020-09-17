import numpy as np
import sys
sys.path.append("..")
from DataAnalysis.tools import get_step_parameters

def data2fopdt(time, speed_cmd, speed):
	[k_td, k_ts, k_tf] = get_step_parameters(time, speed, debug = False, debug_time = 0)
	speed_tmp = np.copy(speed)
	speed_tmp[0:k_td] = 0*speed_tmp[0:k_td]
	for i in range(k_td, k_ts):
		if speed_tmp[i]>speed_tmp[k_ts+200]:
			speed_tmp[i] = speed_tmp[k_ts+200]
	return [time[0:k_tf], speed_cmd[0:k_tf], speed_tmp[0:k_tf]]

def underSampling(time, speed_cmd, speed, DELTA):
	N = len(time)
	time_tmp = []
	speed_cmd_tmp = []
	speed_tmp = []
	print("Initial Samples: ", N)
	for i in range(0, N):
		if time[i]<0.05:
			time_tmp.append(time[i])
			speed_cmd_tmp.append(speed_cmd[i])
			speed_tmp.append(speed[i])
		elif i%DELTA == 0:
			time_tmp.append(time[i])
			speed_cmd_tmp.append(speed_cmd[i])
			speed_tmp.append(speed[i])
	print("Final Samples: ", len(time_tmp))
	return [np.array(time_tmp), np.array(speed_cmd_tmp), np.array(speed_tmp)]