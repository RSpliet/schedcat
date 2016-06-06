#!/usr/bin/python
import schedcat.model.tasks as tasks
import schedcat.overheads.model as m
import schedcat.overheads.fp as fp
import schedcat.sched.edf as edf
import random

from schedcat.util.math import const

#def charge_sched_overheads_np(tasks.TaskSystem ts, fp.Overheads o):

def UUniFast(n, U_sum):
    U = []
    sumU = U_sum
    for i in range(0, n-1):
        nextSumU = sumU * (random.random() ** (1.0 / (n - i)))
        U.append(sumU - nextSumU)
        sumU=nextSumU
    
    U.append(sumU)
    
    return U

def ts_random(n, U_sum, wgs):
    while 1:
        ts = tasks.TaskSystem()
        U = UUniFast(n, U_sum)
        
        for i in range(0, n):
            p = random.randint(1000, 15000)
            c = int(p * U[i])
            if c == 0: # Cost of zero leads to other problems
                break
            
            task = tasks.SporadicTask(c,p)
            task.wc_blocking = c / wgs
            ts.append(task)
        
        if len(ts) != n:
            continue
        
        if ts.utilization() > (U_sum - 0.001) and ts.utilization() <= U_sum:
            break
    
    return ts

def ts_test(ts):
    #global b_np_qpa
        
    for t in ts:
        t.wss = 0
    
    if edf.is_schedulable(1, ts):
        return 1
    
    return 0

# Blckknght, 2016. Source: stackoverflow
def float_range(start,stop,step):
    x = start
    my_list = []
    if step > 0:
        while x < stop:
            my_list.append(x)
            x += step
    else: # should really be if step < 0 with an extra check for step == 0 
        while x > stop:
            my_list.append(x)
            x += step
    return my_list

def custom_range():
    my_list = range(2,10)+range(10,60,10)+range(60,201,20)
    print my_list
    return my_list

#main
o_np_avg = m.Overheads()
o_np_avg.zero_overheads()
o_np_avg.ctx_switch = const(27)

o_np_max = m.Overheads()
o_np_max.zero_overheads()
o_np_max.ctx_switch = const(44)

for wgs in custom_range():
    global u
    u_no = 0.0
    u_avg = 0.0
    u_max = 0.0
    u_no_99 = 0.0
    u_avg_99 = 0.0
    u_max_99 = 0.0
    
    for u in float_range(0.2, 1.01, 0.01):
        b_lp = 0
        b_lp_avg = 0
        b_lp_max = 0
        
        for i in range(0, 50000):
            ts = ts_random(3, u, wgs);
            
            if u_no == 0.0:
                b_lp += ts_test(ts)
            
            if u_avg == 0.0:
                ts_lp_avg = fp.charge_scheduling_overheads(o_np_avg, 1,  False, ts.copy())
                b_lp_avg += ts_test(ts_lp_avg)
            
            if u_max == 0.0:
                ts_lp_max = fp.charge_scheduling_overheads(o_np_max, 1,  False, ts.copy())
                b_lp_max += ts_test(ts_lp_max)
        # endfor       
        
        if u_no == 0.0 and b_lp < 45000:
            u_no = u - 0.01
            
        if u_no_99 == 0.0 and b_lp < 49500:
            u_no_99 = u - 0.01

        if u_avg == 0.0 and b_lp_avg < 45000:
            u_avg = u - 0.01
        
        if u_avg_99 == 0.0 and b_lp_avg < 49500:
            u_avg_99 = u - 0.01

        if u_max == 0.0 and b_lp_max < 45000:
            u_max = u - 0.01
            
        if u_max_99 == 0.0 and b_lp_max < 49500:
            u_max_99 = u - 0.01

        if u_no > 0.0 and u_avg > 0.0 and u_max > 0.0:
            break
    # endfor    

    if u_no == 0.0:
        u_no = 1.0
        
    if u_avg == 0.0:
        u_avg = 1.0
    
    if u_max == 0.0:
        u_max = 1.0
        
    if u_no_99 == 0.0:
        u_no_99 = 1.0
        
    if u_avg_99 == 0.0:
        u_avg_99 = 1.0
    
    if u_max_99 == 0.0:
        u_max_99 = 1.0
    
    print "{0} {1} {2} {3} {4} {5} {6}".format(wgs, u_no, u_no_99, u_avg, u_avg_99, u_max, u_max_99)
