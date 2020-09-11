import pandas
import sys
import numpy as np
sys.path.append("..")
from Visualization.monitor import Monitor
from tools import getLSR

# read data
path = "processed_data/"
file = "2020-08-29 14-56-29[0-511-1Delta[cmd]steps].csv"
data = pandas.read_csv(path+file)

speeds_cmds = data['speeds_cmds[cmd]'].values
ssvs = data['steady_response[RPM]'].values
K_ini = data['FOPDT_k[RPM/cmd]'].values
taus = data['FOPDT_tau[s]'].values
dead_time = data['FOPDT_deadTime[s]'].values

# Pre filter
for i in range(0, len(ssvs)):
	if ssvs[i]>6800:
		ssvs[i] = 6553

# Operating Areas
z0 = 1
z1, = np.where(speeds_cmds == 200)[0]
z2, = np.where(speeds_cmds == 300)[0]
z3 = len(speeds_cmds)-1

# Speed vs cmd LSR: speed = f(cmd) = m*cmd + b
[m1_sp, b1_sp] = getLSR(speeds_cmds, ssvs, z0, z1)
ssvs_lsr1 = m1_sp * speeds_cmds[z0:z1] + b1_sp
ssvs_rmse1 = np.sqrt(np.mean((ssvs_lsr1 - ssvs[z0:z1])**2))
print("SSVS LSR 1 Coefficients:")
print("m = %4.2f [RPM/cmd]\t b = %4.2f [RPM]" %(m1_sp, b1_sp))
print("SSVS RMSE 1: %4.2f [RPM]" %(ssvs_rmse1))

[m2_sp, b2_sp] = getLSR(speeds_cmds, ssvs, z1, z2)
ssvs_lsr2 = m2_sp * speeds_cmds[z1:z2] + b2_sp
ssvs_rmse2 = np.sqrt(np.mean((ssvs_lsr2 - ssvs[z1:z2])**2))
print("SSVS LSR 2 Coefficients:")
print("m = %4.2f [RPM/cmd]\t b = %4.2f [RPM]" %(m2_sp, b2_sp))
print("SSVS RMSE 2: %4.2f [RPM]" %(ssvs_rmse2))

[m3_sp, b3_sp] = getLSR(speeds_cmds, ssvs, z2, z3)
ssvs_lsr3 = m3_sp * speeds_cmds[z2:z3] + b3_sp
ssvs_rmse3 = np.sqrt(np.mean((ssvs_lsr3 - ssvs[z2:z3])**2))
print("SSVS LSR 3 Coefficients:")
print("m = %4.2f [RPM/cmd]\t b = %4.2f [RPM]" %(m3_sp, b3_sp))
print("SSVS RMSE 3: %4.2f [RPM]" %(ssvs_rmse3))

# K vs cmd LSR: K = f(cmd) = m*cmd + b
[m1_K, b1_K] = getLSR(speeds_cmds, K_ini, z0, z1)
K_lsr1 = m1_K * speeds_cmds[z0:z1] + b1_K
K_rmse1 = np.sqrt(np.mean((K_lsr1 - K_ini[z0:z1])**2))
print("K LSR 1 Coefficients:")
print("m = %4.4f [RPM/(cmd^2)]\t b = %4.2f [RPM/cmd]" %(m1_K, b1_K))
print("K RMSE 1: %4.2f [RPM]" %(K_rmse1))

[m2_K, b2_K] = getLSR(speeds_cmds, K_ini, z1, z2)
K_lsr2 = m2_K * speeds_cmds[z1:z2] + b2_K
K_rmse2 = np.sqrt(np.mean((K_lsr2 - K_ini[z1:z2])**2))
print("K LSR 2 Coefficients:")
print("m = %4.4f [RPM/(cmd^2)]\t b = %4.2f [RPM/cmd]" %(m2_K, b2_K))
print("K RMSE 2: %4.2f [RPM]" %(K_rmse2))

[m3_K, b3_K] = getLSR(speeds_cmds, K_ini, z2, z3)
K_lsr3 = m3_K * speeds_cmds[z2:z3] + b3_K
K_rmse3 = np.sqrt(np.mean((K_lsr3 - K_ini[z2:z3])**2))
print("K LSR 3 Coefficients:")
print("m = %4.4f [RPM/(cmd^2)]\t b = %4.2f [RPM/cmd]" %(m3_K, b3_K))
print("K RMSE 3: %4.2f [RPM]" %(K_rmse3))

# tau vs cmd LSR: tau = f(cmd) = m*cmd + b
[m1_tau, b1_tau] = getLSR(speeds_cmds, taus, z0, z1)
tau_lsr1 = m1_tau * speeds_cmds[z0:z1] + b1_tau
tau_rmse1 = np.sqrt(np.mean((tau_lsr1 - taus[z0:z1])**2))
print("tau LSR 1 Coefficients:")
print("m = %4.4f [s/cmd]\t b = %4.2f [s]" %(m1_tau, b1_tau))
print("tau RMSE 1: %4.2f [RPM]" %(tau_rmse1))

[m2_tau, b2_tau] = getLSR(speeds_cmds, taus, z1, z2)
tau_lsr2 = m2_tau * speeds_cmds[z1:z2] + b2_tau
tau_rmse2 = np.sqrt(np.mean((tau_lsr2 - taus[z1:z2])**2))
print("tau LSR 2 Coefficients:")
print("m = %4.4f [s/cmd]\t b = %4.2f [s]" %(m2_tau, b2_tau))
print("tau RMSE 2: %4.2f [RPM]" %(tau_rmse2))

[m3_tau, b3_tau] = getLSR(speeds_cmds, taus, z2, z3)
tau_lsr3 = m3_tau * speeds_cmds[z2:z3] + b3_tau
tau_rmse3 = np.sqrt(np.mean((tau_lsr3 - taus[z2:z3])**2))
print("tau LSR 3 Coefficients:")
print("m = %4.4f [s/cmd]\t b = %4.2f [s]" %(m3_tau, b3_tau))
print("tau RMSE 3: %4.2f [RPM]" %(tau_rmse3))

# deadtime vs cmd LSR: K = f(cmd) = m*cmd + b
[m1_dt, b1_dt] = getLSR(speeds_cmds, dead_time, z0, z1)
dt_lsr1 = m1_dt * speeds_cmds[z0:z1] + b1_dt
dt_rmse1 = np.sqrt(np.mean((dt_lsr1 - dead_time[z0:z1])**2))
print("dead time LSR 1 Coefficients:")
print("m = %4.5f [s/cmd]\t b = %4.2f [s]" %(m1_dt, b1_dt))
print("dead time RMSE 1: %4.2f [RPM]" %(dt_rmse1))

[m2_dt, b2_dt] = getLSR(speeds_cmds, dead_time, z1, z2)
dt_lsr2 = m2_dt * speeds_cmds[z1:z2] + b2_dt
dt_rmse2 = np.sqrt(np.mean((dt_lsr2 - dead_time[z1:z2])**2))
print("dead time LSR 2 Coefficients:")
print("m = %4.5f [s/cmd]\t b = %4.2f [s]" %(m2_dt, b2_dt))
print("dead time RMSE 2: %4.2f [RPM]" %(dt_rmse2))

[m3_dt, b3_dt] = getLSR(speeds_cmds, dead_time, z2, z3)
dt_lsr3 = m3_dt * speeds_cmds[z2:z3] + b3_dt
dt_rmse3 = np.sqrt(np.mean((dt_lsr3 - dead_time[z2:z3])**2))
print("dead time LSR 3 Coefficients:")
print("m = %4.5f [s/cmd]\t b = %4.2f [s]" %(m3_dt, b3_dt))
print("dead time RMSE 3: %4.2f [RPM]" %(dt_rmse3))


# Graph data
steady_mon = Monitor([speeds_cmds, speeds_cmds[z0:z1], speeds_cmds[z1:z2], speeds_cmds[z2:z3]], [ssvs, ssvs_lsr1, ssvs_lsr2, ssvs_lsr3], "Speed step response steady states w.r.t speed cmd", "speed[RPM]", "speed[cmd]", marker="*...", sig_name = ["mean_steady", "lsr1", "lsr2", "lsr3"])
steady_mon.plot()

K_mon = Monitor([speeds_cmds, speeds_cmds[z0:z1], speeds_cmds[z1:z2], speeds_cmds[z2:z3]], [K_ini, K_lsr1, K_lsr2, K_lsr3], "Speed step steady constant K states w.r.t speed cmd", "const[RPM/cmd]", "speed[cmd]", marker="*...", sig_name = ["mean_steady", "K1", "K2", "K3"])
K_mon.plot()

taus_mon = Monitor([speeds_cmds, speeds_cmds[z0:z1], speeds_cmds[z1:z2], speeds_cmds[z2:z3]], [taus, tau_lsr1, tau_lsr2, tau_lsr3], "Speed step taus values w.r.t speed cmd", "tau[s]", "speed[cmd]", marker="*...", sig_name = ["tau", "tau1", "tau2", "tau3"])
taus_mon.plot()

dt_mon = Monitor([speeds_cmds, speeds_cmds[z0:z1], speeds_cmds[z1:z2], speeds_cmds[z2:z3]], [dead_time, dt_lsr1, dt_lsr2, dt_lsr3], "Speed step dead_time values w.r.t speed cmd", "dead_time[s]", "speed[cmd]", marker="*...", sig_name = ["dead_time", "deadtime1", "deadtime2", "deadtime3"])
dt_mon.plot()
dt_mon.show()