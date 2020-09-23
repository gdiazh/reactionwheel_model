import pandas
import numpy as np
import glob
from subprocess import Popen, PIPE
import sys
sys.path.append("..")
from Visualization.monitor import Monitor

path = "data/"

speeds = np.linspace(60, 511, 512-60)
# Data columns
gbl_time =  []
opt_success =  []
opt_iterations =  []
SSE_initial =  []
SSE_final =  []
SSE_improvement =  []
K0 =  []
tau0 =  []
deadtime0 =  []
K =  []
tau =  []
deadtime =  []

for i in range(0, len(speeds)):
	file = glob.glob(path+"*-cmd"+str(speeds[i])+"*.csv")
	data = pandas.read_csv(file[0])
	# get colums data
	gbl_time.append(data['gbl_time'].values)
	opt_success.append(data['opt_success'].values)
	opt_iterations.append(data['opt_iterations'].values)
	SSE_initial.append(data['SSE_initial'].values)
	SSE_final.append(data['SSE_final'].values)
	SSE_improvement.append(data['SSE_improvement'].values)
	K0.append(data['K0[RPM/cmd]'].values)
	tau0.append(data['tau0[s]'].values)
	deadtime0.append(data['deadtime[s]'].values)
	K.append(data['K[RPM/cmd]'].values)
	tau.append(data['tau[s]'].values)
	deadtime.append(data['deadtime[s]'].values) #Todo: solve issue sata saved with same key


# Graph data

K_ini_mon = Monitor([speeds, speeds], [K0, K], "Speed step steady constant K states w.r.t speed cmd", "const[RPM/cmd]", "speed[cmd]", marker="..", sig_name = ["K0", "K"])
K_ini_mon.plot()

dead_time_mon = Monitor([speeds, speeds], [deadtime0, deadtime], "Speed step dead_time values w.r.t speed cmd", "dead_time[s]", "speed[cmd]", sig_name = ["dead_time0", "dead_time"])
dead_time_mon.plot()

taus_mon = Monitor([speeds, speeds], [tau0, tau], "Speed step taus values w.r.t speed cmd", "tau[s]", "speed[cmd]", sig_name = ["tau0", "tau"])
taus_mon.plot()

gbltime_mon = Monitor([speeds], [gbl_time], "Global optimizer execution time w.r.t speed cmd", "exec. time [s]", "speed [cmd]", sig_name = ["gbl_time"])
gbltime_mon.plot()

optiterations_mon = Monitor([speeds], [opt_iterations], "Global optimizer iterations w.r.t speed cmd", "iterations [-]", "speed [cmd]", sig_name = ["iterations"])
optiterations_mon.plot()

SSEimprovement_mon = Monitor([speeds], [SSE_improvement], "Global optimizer improvement w.r.t speed cmd", "improvement [%]", "speed [cmd]", sig_name = ["improvement"])
SSEimprovement_mon.plot()

SSEimprovement_mon.show()