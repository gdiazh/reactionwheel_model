import numpy as np
import sys
sys.path.append("..")
from Visualization.monitor import Monitor

def find_step(t, step_response, debug = False):
    n = len(step_response)
    delta = np.zeros(n)
    for i in range(0, n-2):
        delta[i] = step_response[i+2] - step_response[i]
        if delta[i]>300:
            delta[i] = 0
        if delta[i]<-2000 and t[i]<5:
            delta[i] = 0
    step_size = np.max(delta)
    k = np.argmax(delta) + 2000
    k2 = np.argmin(delta)
    offset = []
    t_offset = []
    steady = []
    t_steady = []
    if debug:
        print("delta=", delta)
        print("np.argmax(delta)=", np.argmax(delta))
        print("np.argmin(delta)=", np.argmin(delta))
        print("delta(argmax)=", delta[np.argmax(delta)])
        print("delta(argmin)=", delta[np.argmin(delta)])
        print("t(argmin)=", t[np.argmin(delta)])
        print("k=", k)
        print("k2=", k2)
    if k == 0:
        stp = Monitor([t, t], [step_response, delta], "Step response", "step[]", "time[s]", sig_name = ["raw", "steady"])
        stp.plot()
        stp.show()
        raise Exception('No Step Found')
    elif k2>k and min(delta)<-30:
        offset = step_response[0:k-50]
        t_offset = t[0:k-50]
        steady = step_response[k:k2]
        t_steady = t[k:k2]
        if debug:
            stp = Monitor([t, t_steady, t_offset, t], [step_response, steady, offset, delta], "Step response", "step[]", "time[s]", sig_name = ["raw", "steady", "offset", "delta"])
            stp.plot()
            stp.show()
    else:
        offset = step_response[0:k-2000]
        t_offset = t[0:k-2000]
        steady = step_response[k:n]
        t_steady = t[k:n]
        if debug:
            stp = Monitor([t, t_steady, t_offset, t], [step_response, steady, offset, delta], "Step response", "step[]", "time[s]", sig_name = ["raw", "steady", "offset", "delta"])
            stp.plot()
            stp.show()
    return [offset, steady, t_steady]

def get_step_parameters(time, step_response, debug = False, debug_time = 0):
    N = len(step_response)      # Signal length
    N1 = int(0.001*N)           # Window length
    N2 = N1                     # Window shift
    N3 = 0                      # Window shift
    Nf = int((N-N1)/N2)         # Window iterations
    STEADY_TOLERANCE = 35      #[RPM]
    INITIAL_OVERFLOW = 15000    #[RPM]
    MIN_RESPONSE = 1200         #[RPM]
    MIN_ALIGN_TIME = 1          #[s]
    STEP_TIME = 6               #[s]
    Ta_FOUND = False
    Td_FOUND = False
    Ts_FOUND = False
    Tf_FOUND = False
    k_ta = 0                    # index of align time
    k_td = 0                    # index of dead time
    k_ts = 0                    # index of steady time
    k_tf = 0                    # index of final time

    # Find Parameters
    # for i in range(0, Nf):
    i = 0
    while ((i*N2+N3)+N1<N):
        std = np.std(step_response[(i*N2+N3):(i*N2+N3)+N1])
        mean = np.mean(step_response[(i*N2+N3):(i*N2+N3)+N1])
        # find align time
        if not(Ta_FOUND) and std<STEADY_TOLERANCE and step_response[(i*N2+N3)]<INITIAL_OVERFLOW and time[(i*N2+N3)]>MIN_ALIGN_TIME:
            k_ta = (i*N2+N3)
            Ta_FOUND = True
            if debug:
                print(chr(27)+"[1;31m"+"Align time found at (index): "+chr(27)+"[0m", k_ta)
        # find dead time
        if not(Td_FOUND) and Ta_FOUND and mean>1 and std>10:
            k_td = (i*N2+N3)
            Td_FOUND = True
            N1 = int(0.02*N)        # Increase Window length
            N3 = 10*N2              # Window shift
            if debug:
                print(chr(27)+"[1;31m"+"Dead time found at (index): "+chr(27)+"[0m", k_td)
        # find steady time
        if not(Ts_FOUND) and Td_FOUND and std<STEADY_TOLERANCE and MIN_RESPONSE<mean<INITIAL_OVERFLOW:
            k_ts = (i*N2+N3)
            Ts_FOUND = True
            N1 = int(0.001*N)       # Increase Window length
            N3 = 10*N2              # Window shift
            if debug:
                print(chr(27)+"[1;31m"+"Steady time found at: index "+chr(27)+"[0m", k_ts, chr(27)+"[1;31m"+", time "+chr(27)+"[0m", time[k_ts])
        # find final time
        if not(Tf_FOUND) and Ts_FOUND and (std>60 or mean<1):
            if mean<1:
                k_tf = (i*N2+N3)-50
            else:
                k_tf = (i*N2+N3)
            Tf_FOUND = True
            if debug:
                print(chr(27)+"[1;31m"+"Final time found at (index): "+chr(27)+"[0m", k_tf)
        # plot for debugging
        if debug and time[(i*N2+N3)]>debug_time:
            print(chr(27)+"[0;33m"+"Current Statistics:"+chr(27)+"[0m")
            print("Window iteration: ", i, "/", Nf)
            print("std: ", std)
            print("mean: ", mean)
            print("window_time[0]: ", time[(i*N2+N3)])
            print("window_value[0]: ", step_response[(i*N2+N3)])
            print("window_time[f]: ", time[(i*N2+N3)+N1])
            print("window_value[f]: ", step_response[(i*N2+N3)+N1])
            print("signal_size: ", N)
            print("window_size: ", N1)
            print("window_shift: ", N2)
            stp = Monitor([time, time[(i*N2+N3):(i*N2+N3)+N1]], [step_response, step_response[(i*N2+N3):(i*N2+N3)+N1]], "Step response", "step[]", "time[s]", sig_name = ["raw", "Window"])
            stp.plot()
            stp.show()
        i+=1
    # Check
    if not(Ta_FOUND):
        print("No Align Time Found")
        raise Exception('No Align Time Found')
    elif not(Td_FOUND):
        print("No Dead Time Found")
        raise Exception('No Dead Time Found')
    elif not(Ts_FOUND):
        print("No Steady Time Found")
        raise Exception('No Steady Time Found')
    elif not(Tf_FOUND):
        print("No Final Time Found")
        raise Exception('No Final Time Found')
    else:
        if debug:
            print(chr(27)+"[0;34m"+"Parameters Found"+chr(27)+"[0m")
    return [k_td, k_ts, k_tf]

if __name__ == '__main__':
    # TEST
    import pandas

    path = "../../DRV10987_Firmware/ros_uart_controller/data/steps/"
    # files = path+"2020-08-21 13-50-43[cmd-60.0].csv"
    files = path+"2020-08-21 13-50-54[cmd-61.0].csv"
    # files = path+"2020-08-21 13-52-01[cmd-67.0].csv"
    # files = path+"2020-08-21 13-53-29[cmd-75.0].csv"
    # files = path+"2020-08-21 13-51-05[cmd-62.0].csv"
    # files = path+"2020-08-21 13-52-12[cmd-68.0].csv"
    # files = path+"2020-08-21 13-57-00[cmd-94.0].csv"
    # files = path+"2020-08-21 13-57-44[cmd-98.0].csv"
    data = pandas.read_csv(files)
    times = data['time[s]'].values
    speeds = data['speed[RPM]'].values
    [k_td, k_ts, k_tf] = get_step_parameters(times, speeds, debug = True, debug_time = 5)
    stp = Monitor([times, times[0:k_td], times[k_ts:k_tf]], [speeds, speeds[0:k_td], speeds[k_ts:k_tf]], "Step response", "speed[RPM]", "time[s]", sig_name = ["raw", "dead_time", "steady"])
    stp.plot()
    stp.show()