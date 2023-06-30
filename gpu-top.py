from prettytable import PrettyTable
import subprocess
import re

gpu_stats = subprocess.getoutput("nvidia-smi").split('\n')
n_line = len(gpu_stats)
print(gpu_stats[0])


# GPU INFO
gpu_table = PrettyTable()
gpu_table.vrules = 0
gpu_table.field_names = ['GPU', 'Fan', 'Temp', 'Perf', 'Pwr:Usage/Cap', 'Memory-Usage', 'Utilization']

# find gpu info start
i = 1
while i < n_line and not gpu_stats[i].startswith("|=="):
    i += 1
i += 1

# parse gpu info
while i < n_line:
    if gpu_stats[i].startswith("+--"):
        i += 1
    elif gpu_stats[i].startswith("|            "):
        i += 1
    elif gpu_stats[i].startswith("|"):
        gpu_id = int(gpu_stats[i][1:5])
        gpu_info = gpu_stats[i+1].split('|')
        gpu_info_part1 = gpu_info[1].split()
        gpu_fan = gpu_info_part1[0]
        gpu_temp = gpu_info_part1[1]
        gpu_perf = gpu_info_part1[2]
        gpu_pwr = ' '.join(gpu_info_part1[3:]).rjust(10)
        gpu_mem = gpu_info[2].strip().rjust(19)
        gpu_utl = gpu_info[3][:8].strip().rjust(11)
        cur_gpu_data = [gpu_id, gpu_fan, gpu_temp, gpu_perf, gpu_pwr, gpu_mem, gpu_utl]
        gpu_table.add_row(cur_gpu_data)
        i += 2
    else:
        break

# print table
print(gpu_table)


# PID INFO
pid_table = PrettyTable()
pid_table.vrules = 0
#pid_table.align = "l"
pid_table.field_names = ['GPU', 'PID', 'User', 'Process name', 'Memory']

# find pid info start
while i < n_line and not gpu_stats[i].startswith("|=="):
    i += 1
i += 1

# print pid info
pid_results = []
pids = []
while i < n_line:
    if gpu_stats[i].startswith("+--") or gpu_stats[i].startswith("|  No"):
        i += 1
    elif gpu_stats[i].startswith("|"):
        pid_info = re.split(r'\s+', gpu_stats[i])
        gpu_id = pid_info[1]
        pid = pid_info[4]
        try:
            x = int(pid)
        except:
            pid = pid_info[2]
        pmem = pid_info[-2]
        pid_results.append((gpu_id, pid, pmem))
        pids.append(pid)
        i += 1
    else:
        break

if len(pids) > 0:
    pid_stats = subprocess.getoutput("ps -o pid,user:14,cmd -p {}".format(",".join(pids))).split('\n')
    pid_pair = [re.split(r'\s+', line.strip(), 2) for line in pid_stats[1:]]
    pid2user = {pair[0]: pair[1] for pair in pid_pair}
    pid2cmd = {pair[0]: pair[2] for pair in pid_pair}
    for gpu_id, pid, pmem in pid_results:
        try:
            pid_table.add_row([gpu_id.rjust(3), pid.rjust(7), pid2user[pid][:14], pid2cmd[pid][:37], pmem.rjust(9)])
        except:
            pass
        
if len(pids) > 0:
    print(pid_table)
else:
    print("-- No running processes found\n")
