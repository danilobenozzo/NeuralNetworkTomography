#=======================IMPORT THE NECESSARY LIBRARIES=========================
import subprocess
import time
import os
#==============================================================================

#================================INITIALIZATIONS===============================
os.chdir('..')
os_name = os.name
if os_name == 'posix':
    shell_flag = True
else:
    shell_flag = False
#==============================================================================


#================================PLOT THE FIGURE===============================
query_str = 'python Plot_Results.py -E "50" -I "10" -L 1 -P "0.4" -D "10" -Q 0.1 -M 3 -f "B" -K N -O "1041,2082,3123,4164,5205,6246"'
proc = subprocess.Popen(query_str,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell_flag)
#==============================================================================


