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
