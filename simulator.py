'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import copy
import queue

input_file = 'input.txt'
def SRTF_lt(process_a, process_b):
    return process_a.burst_time < process_b.burst_time or process_a.burst_time == process_b.burst_time and process_a.arrive_time < process_b.arrive_time

def SJF_lt(process_a, process_b):
    return process_a.pred_time < process_b.pred_time or process_a.pred_time == process_b.pred_time and process_a.arrive_time < process_b.arrive_time

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time, lt=SRTF_lt):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.lt = lt
        self.pred_time = 0

    def __lt__(self, other):
        return self.lt(self, other)
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list_origin, time_quantum):
    schedule = []
    current_time = 0
    waiting_time = 0
    process_pool = {}
    process_ids = []
    process_index = 0
    process_list = copy.deepcopy(process_list_origin)

    while process_ids or process_list:
        while process_list and process_list[0].arrive_time<=current_time:
            process = process_list.pop(0)
            if process.id in process_pool:
                process_pool[process.id].append(process)
            else:
                process_pool[process.id] = [process]
            if process.id not in process_ids:
                process_ids.append(process.id)

        if not process_ids:
            current_time = process_list[0].arrive_time
            continue
        if process_index>=len(process_ids):
            process_index = 0
        current_pool = process_pool[process_ids[process_index]]
        if(len(current_pool)>0):
            current_process = current_pool[0]
            process_index = process_index+1

            if(not schedule or pre_process != current_process):
                schedule.append((current_time, current_process.id))
            waiting_time = waiting_time + (current_time - current_process.arrive_time)

            if(current_process.burst_time<=time_quantum):
                current_time += current_process.burst_time
                process_pool[current_process.id].pop(0)
            else:
                current_time += time_quantum
                current_process.burst_time-=time_quantum
                current_process.arrive_time = current_time
            pre_process = current_process
        else:
            process_ids.pop(process_index)


    average_waiting_time = waiting_time / float(len(process_list_origin))
    return schedule, average_waiting_time
    # return (["to be completed, scheduling process_list on round robin policy with time_quantum"], 0.0)

def SRTF_scheduling(process_list_origin):
    schedule = []
    pqueue = queue.PriorityQueue()
    current_time = 0
    waiting_time = 0
    process_list = copy.deepcopy(process_list_origin)

    while not pqueue.empty() or process_list:
        if pqueue.empty():
            new_process = process_list.pop(0)
            pqueue.put(new_process)
            current_time = new_process.arrive_time

        else:
            current_process = pqueue.get()
            if (not schedule or current_process != pre_process):
                schedule.append((current_time, current_process.id))
            waiting_time = waiting_time + (current_time - current_process.arrive_time)

            if process_list:
                next_arrival_process = process_list[0]
                if next_arrival_process.arrive_time <= current_process.arrive_time + current_process.burst_time:
                    pqueue.put(process_list.pop(0))

                    if(next_arrival_process.arrive_time < current_time + current_process.burst_time):
                        current_process.burst_time -= next_arrival_process.arrive_time - current_time
                        current_process.arrive_time = next_arrival_process.arrive_time
                        pqueue.put(current_process)
                    current_time = next_arrival_process.arrive_time
                else:
                    current_time += current_process.burst_time
            else:
                current_time +=current_process.burst_time
            pre_process = current_process


    average_waiting_time = waiting_time / float(len(process_list_origin))
    return schedule, average_waiting_time
    # return (["to be completed, scheduling process_list on SRTF, using process.burst_time to calculate the remaining time of the current process "], 0.0)

def SJF_scheduling(process_list_origin, alpha=0.5, init_time=5):
    schedule = []
    pqueue = queue.PriorityQueue()
    current_time = 0
    waiting_time = 0
    process_list = copy.deepcopy(process_list_origin)
    pred_history = {}

    while not pqueue.empty() or process_list:
        while (process_list and process_list[0].arrive_time <= current_time):
            process = process_list.pop(0)
            if process.id in pred_history:
                new_pred = alpha*pred_history[process.id][1]+(1-alpha)*pred_history[process.id][0]
                pred_history[process.id] = [new_pred,process.burst_time]
            else:
                pred_history[process.id] = [init_time, process.burst_time]

            process.pred_time = pred_history[process.id][0]
            process.lt = SJF_lt
            pqueue.put(process)
        if pqueue.empty():
            current_time = process_list[0].arrive_time
            continue

        current_process = pqueue.get()
        if (not schedule or current_process != pre_process):
            schedule.append((current_time, current_process.id))
        waiting_time = waiting_time + (current_time - current_process.arrive_time)
        current_time += current_process.burst_time
        pre_process = current_process

    average_waiting_time = waiting_time / float(len(process_list_origin))
    return schedule, average_waiting_time
    # return (["to be completed, scheduling SJF without using information from process.burst_time"],0.0)



def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

