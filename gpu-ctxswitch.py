#!/usr/bin/python
import schedcat.model.tasks as tasks
import schedcat.overheads.model as m
import schedcat.overheads.fp as fp
import schedcat.sched.edf as edf
import random

from schedcat.util.math import const

b = 0
b_np = 0
avg_np = 0
max_np = 0
avg_p = 0
max_p = 0

#def charge_sched_overheads_np(tasks.TaskSystem ts, fp.Overheads o):
def charge_sched_overheads_np(o, ts):
    for t in ts:
        # For non-preemptive systems, The "end of task" event always corresponds
        # with the "start of task" event of a different task. Hence context
        # switching overhead is limited to 1*cost
        t.cost += o.ctx_switch(ts)
        
    return ts
    
def make_np(ts):
    for t in ts:
        t.wc_blocking = t.cost
        
    return ts

def make_lp(ts):
    for t in ts:
        # Give each task a blocking time based on a random number of workgroups
        wgs = random.randint(5, 500)
        t.wc_blocking = t.cost / wgs
        
    return ts

def UUniFast(n, U_sum):
    U = []
    sumU = U_sum
    for i in range(0, n-1):
        nextSumU = sumU * (random.random() ** (1.0 / (n - i)))
        U.append(sumU - nextSumU)
        sumU=nextSumU
    
    U.append(sumU)
    
    return U

def ts_random(n, U_sum):
    while 1:
        ts = tasks.TaskSystem()
        U = UUniFast(n, U_sum)
        
        for i in range(0, n):
            p = random.randint(1000, 15000)
            c = int(p * U[i])
            if c == 0: # Cost of zero leads to other problems
                break    
            ts.append(tasks.SporadicTask(c, p))
        
        if len(ts) != n:
            continue
        
        if ts.utilization() > (U_sum - 0.001) and ts.utilization() <= U_sum:
            break
    
    return ts

def ts_test(ts):
    global b
    global b_lp
    global b_np
    #global b_np_qpa
    global avg_np
    global max_np
    global avg_lp
    global max_lp
    global avg_p
    global max_p
    global printed_example
    
    o_np_avg = m.Overheads()
    o_np_avg.zero_overheads()
    o_np_avg.ctx_switch = const(27)
    
    o_np_max = m.Overheads()
    o_np_max.zero_overheads()
    o_np_max.ctx_switch = const(44)
    
    o_p_avg = m.Overheads()
    o_p_avg.zero_overheads()
    o_p_avg.ctx_switch = const(263)
    
    o_p_max = m.Overheads()
    o_p_max.zero_overheads()
    o_p_max.ctx_switch = const(434)
    
    for t in ts:
        t.wss = 0
    
    ts_np = make_np(ts.copy())
    ts_lp = make_lp(ts.copy())
    ts_np_avg = charge_sched_overheads_np(o_np_avg, ts_np.copy())
    ts_np_max = charge_sched_overheads_np(o_np_max, ts_np.copy())
    ts_lp_avg = fp.charge_scheduling_overheads(o_np_avg, 1,  False, ts_lp.copy())
    ts_lp_max = fp.charge_scheduling_overheads(o_np_max, 1,  False, ts_lp.copy())
    ts_p_avg = fp.charge_scheduling_overheads(o_p_avg, 1,  False, ts.copy())
    ts_p_max = fp.charge_scheduling_overheads(o_p_max, 1,  False, ts.copy())
    
    if edf.is_schedulable(1, ts):
        b += 1
    #if edf.is_schedulable(1, ts, preemptive=False):
    #    b_np += 1
    if edf.is_schedulable(1, ts_lp):
        b_lp += 1
    if edf.is_schedulable(1, ts_np):
        b_np += 1
    if edf.is_schedulable(1, ts_np_avg):
        avg_np += 1
    if edf.is_schedulable(1, ts_np_max):
        max_np += 1
    if edf.is_schedulable(1, ts_lp_avg):
        avg_lp += 1
    if edf.is_schedulable(1, ts_lp_max):
        max_lp += 1
    if edf.is_schedulable(1, ts_p_avg):
        avg_p += 1
    if edf.is_schedulable(1, ts_p_max):
        max_p += 1

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

#main
for u in float_range(0.2, 1.01, 0.01):
    b = 0
    b_np = 0
    b_lp = 0
   # b_np_qpa = 0
    avg_np = 0
    max_np = 0
    avg_lp = 0
    max_lp = 0
    avg_p = 0
    max_p = 0
    
    for i in range(0, 100000):
        ts_test(ts_random(2, u))
    
    print "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(u, b, avg_p, max_p,
                                b_lp, avg_lp, max_lp, b_np, avg_np, max_np)
