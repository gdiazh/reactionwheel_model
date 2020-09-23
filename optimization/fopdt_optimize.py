import pandas
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import minimize
from scipy.interpolate import interp1d
from tools import data2fopdt
from tools import underSampling
from timeit import default_timer as timer
import sys
sys.path.append("..")
from Visualization.monitor import Monitor

# Input data parameters
print(chr(27)+"[1;31m"+"FOPDT Optimization"+chr(27)+"[0m")
file = input("File name (*.csv): ")
file_cmd = input("File cmd: ")
# read raw data
path = "../../DRV10987_Firmware/ros_uart_controller/data/steps/"
data = pandas.read_csv(path+file)
time = data['time[s]'].values
speed_cmd = data['speed[cmd]'].values
speed = data['speed[RPM]'].values

# read processed data
path = "../DataAnalysis/processed_data/"
file = "2020-08-29 14-56-29[0-511-1Delta[cmd]steps].csv"
data = pandas.read_csv(path+file)
speeds_cmds = data['speeds_cmds[cmd]'].values
K_ini = data['FOPDT_k[RPM/cmd]'].values
taus = data['FOPDT_tau[s]'].values
dead_time = data['FOPDT_deadTime[s]'].values

# Fix data to match a first order system
[time_fit, speed_cmd_fit, speed_fit] = data2fopdt(time, speed_cmd, speed) #[s, cmd, RPM]

dfit = Monitor([time_fit, time, time_fit], [speed_cmd_fit,  speed, speed_fit], "Speed step response pre fitting", "speed[RPM, cmd]", "time[s]", sig_name = ["speed_cmd_fit", "speed", "speed_fit"])
dfit.plot()
dfit.show()

# UnderSampling data to decrease optimizer execution time
[time_us, speed_cmd_us, speed_us] = underSampling(time_fit, speed_cmd_fit, speed_fit, 80) #[s, cmd, RPM]

dfit = Monitor([time_us, time, time_us], [speed_cmd_us,  speed, speed_us], "Speed step response underSampled", "speed[RPM, cmd]", "time[s]", marker="...", sig_name = ["speed_cmd_us", "speed", "speed_us"])
dfit.plot()
dfit.show()

# Optimization variables
u0 = speed_cmd_us[0]           # Ininial input cmd value [cmd]
yp0 = speed_us[0]              # Initial output speed value [RPM]
t = time_us                    # time [s]
u = speed_cmd_us               # system input
yp = speed_us                  # system output

ns = len(t)                 # number of data point
delta_t = t[1]-t[0]         # time step [s]

uf = interp1d(t,u, fill_value="extrapolate")          # input vector time interpolation

DEBUG = False

def fopdt(y, t, uf, Km, taum, deadtimem):
    """
    * First Order Plus Dead Time model
    *
    * @param y         np.array(n) system output
    * @param t         np.array(n) system time
    * @param uf        ???         input linear function (for time shift)
    * @param Km        Float       model gain
    * @param taum      Float       model time constant
    * @param deadtimem Float       model dead time 
    """
    # Delayed input according to dead time
    if (t-deadtimem) <= 0:
        um = uf(0.0)
    else:
        um = uf(t-deadtimem)
    # Dynamic
    dydt = (Km*(um-u0)-(y-yp0))/taum
    return dydt

def sim_model(x):
    """
    * Simulate FOPDT model
    *
    * @param x         List(3) Model parameters (for which to obtain optimal values)
    * @param x[0]      Float   Km           model gain
    * @param x[1]      Float   taum         model time constant
    * @param x[2]      Float   deadtimem    model dead time
    * @return ym       np.array(n)          model output
    """
    # initial values
    ym = np.zeros(ns)
    ym[0] = yp0
    if DEBUG:
        initial_time = timer()              #[s]
    # Simulate
    for i in range(0, ns-1):
        y_next = odeint(fopdt, ym[i], [t[i], t[i+1]], args=(uf, x[0], x[1], x[2]))
        ym[i+1] = y_next[-1]
    if DEBUG:
        time = timer() - initial_time    #[s]
        print("Simulation time: ", time, "[s]")
    return ym

# define objective
def objective(x):
    # simulate model
    ym = sim_model(x)
    # calculate objective
    obj = np.sum((ym-yp)**2)
    if DEBUG:
        print("Current SSE Objective: ", obj)
    return obj

# initial guesses
print(chr(27)+"[1;31m"+"First Order Plus Dead Time Optimization"+chr(27)+"[0m")
j = int(float(file_cmd))-60
print("Initial Guess:")
print("speed cmd: ", speeds_cmds[j])
print("K: ", K_ini[j])
print("tau: ", taus[j])
print("deadtime: ", dead_time[j])
x0 = np.zeros(3)
x0[0] = K_ini[j]        # Km
x0[1] = taus[j]         # taum
x0[2] = dead_time[j]    # deadtimem

# Statistics
global_time = timer()

# show initial objective
print(chr(27)+"[1;33m"+"Calculating Initial SSE Value ..."+chr(27)+"[0m")
obj0 = objective(x0)
print('Initial SSE Objective: ' + str(obj0))

# optimize Km, taum, deadtimem
print(chr(27)+"[1;33m"+"Running Optimizer ..."+chr(27)+"[0m")
solution = minimize(objective, x0, method = 'L-BFGS-B')
x = solution.x
objf = objective(x)
global_time = timer()-global_time
print(solution.message)

# show final objective
print(chr(27)+"[1;34m"+"Optimizer Finished"+chr(27)+"[0m")
print("Global Optimization Time: %4.2f [s]" %(global_time))
print("Iterations performed: %d" %(solution.nit))
print("Final SSE Objective: " + str(objf))
print("SSE Improvement: %4.1f" % (100*(obj0-objf)/obj0) + " %")
print("K: %4.4f \t K0: %4.4f \t delta K: %4.4f" % (x[0], x0[0], x[0]-x0[0]))
print("tau: %4.4f \t tau0: %4.4f \t delta tau: %4.4f" % (x[1], x0[1], x[1]-x0[1]))
print("deadtime: %4.4f \t deadtime0: %4.4f \t delta deadtime: %4.4f" % (x[2], x0[2], x[2]-x0[2]))

# calculate model with updated parameters
ym1 = sim_model(x0)
ym2 = sim_model(x)

# Save data to csv
SAVE_DATA = True
if SAVE_DATA:
    import pandas as pd
    from pathlib import Path
    import datetime
    folder = "data/"
    Path(folder).mkdir(parents=True, exist_ok=True)
    data = {"gbl_time": global_time,
            "opt_success": solution.success,
            "opt_iterations": solution.nit,
            "SSE_initial": obj0,
            "SSE_final": objf,
            "SSE_improvement": 100*(obj0-objf)/obj0,
            "K0[RPM/cmd]": x0[0], "tau0[s]": x0[1], "deadtime0[s]": x0[2],
            "K[RPM/cmd]": x[0], "tau[s]": x[1], "deadtime[s]": x[2]}
    df = pd.DataFrame(data, columns=["gbl_time", "opt_success", "opt_iterations", "SSE_initial", "SSE_final", "SSE_improvement", "K0[RPM/cmd]", "tau0[s]", "deadtime[s]", "K[RPM/cmd]", "tau[s]", "deadtime[s]"], index=[0])
    test_name = "[optimal-fopdt-params-cmd"+str(speeds_cmds[j])+"]"
    date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    path = Path(folder+date+test_name+".csv")
    df.to_csv(path)

# plot results
dfit = Monitor([t, t, t], [yp,  ym1, ym2], "Speed step response FOPDT fitting", "speed[RPM, cmd]", "time[s]", marker = "x.*", sig_name = ["pre_fit", "initial_guess", "optimized"])
dfit.plot()
dfit.show()