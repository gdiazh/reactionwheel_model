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

data = [None]*len(files)
for i in range(0, len(files)):
	data[i] = pandas.read_csv(files[i])

times = [None]*len(data)
speed_cmds = [None]*len(data)
speeds = [None]*len(data)
for i in range(0, len(data)):
	times[i] = data[i]['time[s]'].values
	speed_cmds[i] = data[i]['speed[cmd]'].values
	speeds[i] = data[i]['speed[RPM]'].values

# Calc Speed steady state values
ssvs_cmd = [None]*len(speeds)
dead_time_cmd = [None]*len(speeds)
taus_cmd = [None]*len(speeds)
for i in range(0, len(speeds)):
	# [s_offset, s_steady, t_steady] = find_step2(times[i], speeds[i], debug = True)
	try:
		[k_td, k_ts, k_tf] = get_step_parameters(times[i], speeds[i], debug = True, debug_time = 1.8)
		# print(chr(27)+"[0;34m"+"Find parameters: "+chr(27)+"[0m", files[i])
	except Exception as e:
		print("Exception on file: ", files[i])
		print(e)
		k_td=0
		k_ts=1
		k_tf=2
		# Exception('Fail getting parameters')
	cmd_ = float(files[i][len(path)+24:-5])
	ssvs_cmd[i] = [cmd_, np.mean(speeds[i][k_ts:k_tf])]
	dead_time_cmd[i] = [cmd_, times[i][k_td]]
	taus_cmd[i] = [cmd_, times[i][k_ts]]

ssvs_cmd.sort()
dead_time_cmd.sort()
taus_cmd.sort()
ssvs_cmd = np.array(ssvs_cmd)
dead_time_cmd = np.array(dead_time_cmd)
taus_cmd = np.array(taus_cmd)

speeds_cmds = ssvs_cmd[:, 0]
ssvs = ssvs_cmd[:, 1]
dead_time = dead_time_cmd[:, 1]
taus = taus_cmd[:, 1]
K_ini = np.divide(ssvs, speeds_cmds)

# Save data to csv
SAVE_DATA = True
if SAVE_DATA:
    import pandas as pd
    from pathlib import Path
    import datetime
    folder = "processed_data/"
    Path(folder).mkdir(parents=True, exist_ok=True)
    data = {"speeds_cmds[cmd]": speeds_cmds, "steady_response[RPM]": ssvs, "FOPDT_k[RPM/cmd]": K_ini, "FOPDT_tau[s]": taus, "FOPDT_deadTime[s]": dead_time}
    df = pd.DataFrame(data, columns=["speeds_cmds[cmd]", "steady_response[RPM]", "FOPDT_k[RPM/cmd]", "FOPDT_tau[s]", "FOPDT_deadTime[s]"])
    test_name = "[0-511-1Delta[cmd]steps]"
    date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    path = Path(folder+date+test_name+".csv")
    df.to_csv(path)

speed_mon = Monitor(times[0:5], speeds[0:5], "Motor speed steps", "w[RPM]", "time[s]", sig_name = ["s60", "s61", "s62", "s63", "s64", "s65", "s66"])
speed_mon.plot()
speed_mon.show()

steady_mon = Monitor([speeds_cmds], [ssvs], "Speed step response steady states w.r.t speed cmd", "speed[RPM]", "speed[cmd]", sig_name = ["mean_steady"])
steady_mon.plot()
steady_mon.show()

K_ini_mon = Monitor([speeds_cmds], [K_ini], "Speed step steady constant K states w.r.t speed cmd", "const[RPM/cmd]", "speed[cmd]", sig_name = ["mean_steady"])
K_ini_mon.plot()
K_ini_mon.show()

dead_time_mon = Monitor([speeds_cmds], [dead_time], "Speed step dead_time values w.r.t speed cmd", "dead_time[s]", "speed[cmd]", sig_name = ["dead_time"])
dead_time_mon.plot()
dead_time_mon.show()

taus_mon = Monitor([speeds_cmds], [taus], "Speed step taus values w.r.t speed cmd", "tau[s]", "speed[cmd]", sig_name = ["tau"])
taus_mon.plot()
taus_mon.show()