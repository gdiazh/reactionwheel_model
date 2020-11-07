import pandas
import sys
sys.path.append("..")
from Visualization.monitor import Monitor

# read data
path = "processed_data/"
file = "2020-11-06 20-17-32[100-511-100[cmd]steps].csv"
data = pandas.read_csv(path+file)

speeds_cmds = data['speeds_cmds[cmd]'].values
ssvs = data['steady_response[RPM]'].values
K_ini = data['FOPDT_k[RPM/cmd]'].values
taus = data['FOPDT_tau[s]'].values
dead_time = data['FOPDT_deadTime[s]'].values

# Graph data
steady_mon = Monitor([speeds_cmds], [ssvs], "Speed step response steady states w.r.t speed cmd", "speed[RPM]", "speed[cmd]", marker="*", sig_name = ["mean_steady"])
steady_mon.plot()

K_ini_mon = Monitor([speeds_cmds], [K_ini], "Speed step steady constant K states w.r.t speed cmd", "const[RPM/cmd]", "speed[cmd]", marker="*", sig_name = ["mean_steady"])
K_ini_mon.plot()

dead_time_mon = Monitor([speeds_cmds], [dead_time], "Speed step dead_time values w.r.t speed cmd", "dead_time[s]", "speed[cmd]", sig_name = ["dead_time"])
dead_time_mon.plot()

taus_mon = Monitor([speeds_cmds], [taus], "Speed step taus values w.r.t speed cmd", "tau[s]", "speed[cmd]", sig_name = ["tau"])
taus_mon.plot()
taus_mon.show()