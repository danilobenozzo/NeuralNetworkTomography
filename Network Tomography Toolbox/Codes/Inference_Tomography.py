#=======================IMPORT THE NECESSARY LIBRARIES=========================
from time import time
import numpy as np
import sys,getopt,os
import resource
try:
    import matplotlib.pyplot as plt
except:
    print 'Matplotlib can not be initiated! Pas de probleme!'
import pdb
from copy import deepcopy
from scipy.cluster.vq import whiten
#from scipy.signal import find_peaks_cwt
import os.path

from CommonFunctions.auxiliary_functions import read_spikes,combine_weight_matrix,combine_spikes_matrix,generate_file_name,spike_binning
from CommonFunctions.auxiliary_functions_inference import *
from CommonFunctions.Neurons_and_Networks import *
# reload(CommonFunctions.auxiliary_functions_inference)
#from sklearn import metrics
import multiprocessing

os.system('clear')                                              # Clear the commandline window
#==============================================================================

#==========================PARSE COMMAND LINE ARGUMENTS========================
input_opts, args = getopt.getopt(sys.argv[1:],"hN:Q:T:S:D:A:F:R:L:M:B:X:Y:C:V:J:U:Z:b:p:j:o:")

T,no_neurons,file_name_spikes,file_name_base_results,inference_method,sparsity_flag,beta,alpha0,max_itr_optimization,no_processes,block_size,bin_size,neuron_range = parse_commands_inf_algo(input_opts)
#==============================================================================


#==================DO SANITY CHECK ON THE ENTERED PARAMETERS===================
if not no_neurons:
    print 'Sorry you should specify the number of observed neurons'
    exit

if not T:
    print 'Sorry you should specify the duration of recorded samples in miliseconds'
    exit
#==============================================================================

#================================INITIALIZATIONS===============================

#---------------------Initialize Simulation Variables--------------------------
theta = .005                                               # The update threshold of the neurons in the network
d_window = 2                                          # The time window the algorithm considers to account for pre-synaptic spikes
sparse_thr0 = 0.0005                                    # The initial sparsity soft-threshold (not relevant in this version)
tau_d = 20.0                                    # The decay time coefficient of the neural membrane (in the LIF model)
tau_s = 2.0                                     # The rise time coefficient of the neural membrane (in the LIF model)

num_process = min(no_processes,multiprocessing.cpu_count())
block_size = min(block_size,T)
#------------------------------------------------------------------------------

#-------------------------Initialize Inference Parameters----------------------
if len(neuron_range)>1:
    neuron_range = range(neuron_range[0],neuron_range[1])

inferece_params = [alpha0,sparse_thr0,sparsity_flag,theta,max_itr_optimization,d_window,beta,bin_size]
#..............................................................................

#------------------------------------------------------------------------------

#==============================================================================


#===============================READ THE SPIKES================================
    
#----------------------------Read and Sort Spikes------------------------------
if not file_name_spikes:
    file_name_spikes = '../Data/Spikes/Moritz_Spike_Times.txt'
    file_name_spikes = '/scratch/salavati/NeuralNetworkTomography/Network Tomography Toolbox/Data/Spikes/Moritz_Spike_Times.txt'
    #file_name_spikes = '../Data/Spikes/HC3_ec013_198_processed.txt'
    #file_name_spikes = '/scratch/salavati/NeuralNetworkTomography/Network Tomography Toolbox/Data/Spikes/HC3_ec013_198_processed.txt'
    
    try:
        ll = file_name_spikes.split('/')
    except:
        ll = file_name_spikes.split('/')
    
    ll = ll[-1]
    file_name_prefix = ll.split('.txt')
#------------------------------------------------------------------------------
        
#---------------------Preprocess the Spikes If Necessary-----------------------
file_name_spikes2 = file_name_spikes[:-4] + '_file.txt'
if not os.path.isfile(file_name_spikes2):            
    out_spikes = np.genfromtxt(file_name_spikes, dtype=float, delimiter='\t')            
    spike_file = open(file_name_spikes2,'w')
    fire_matx = [''] * (T+1)
    LL = out_spikes.shape[0]
    nn = -1
    for l in range(0,LL):
        last_nn = nn
        nn = int(out_spikes[l,0])
        tt = int(1000*out_spikes[l,1])
        if tt<=T:
            temp = fire_matx[tt]
            try:
                if str(nn) not in temp:
                    if len(temp):
                        temp = temp + ' ' + str(nn)
                    else:
                        temp = str(nn)
                else:
                    print 'What the ...?'
                    pdb.set_trace()
                        
                if tt<=T:
                    fire_matx[tt] = temp
            except:
                pdb.set_trace()
    spike_file.write('\n'.join(fire_matx))
    spike_file.close()
#------------------------------------------------------------------------------

#==============================================================================

#============================INFER THE CONNECTIONS=============================
for n_ind in neuron_range:
    
    print 'memory so far %s' %str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    t_start = time.time()                           # starting time of the algorithm
    
    W_inferred,used_ram = inference_constraints_hinge_parallel(file_name_spikes2,T,block_size,n,max_itr_optimization,sparse_thr0,alpha0,theta,n_ind,num_process)
    W_inferred = np.array(W_inferred)
    
    #.........................Save the Belief Matrices.........................
    file_name_ending = 'I_' + str(inference_method) + '_S_' + str(sparsity_flag) + '_T_' + str(T)
    file_name_ending = file_name_ending + '_C_' + str(num_process) + '_B_' + str(block_size)

    if bin_size:
        file_name_ending = file_name_ending + '_bS_' + str(bin_size)
    
    file_name_ending = file_name_ending + '_ii_' + str(max_itr_optimization)
    file_name =  file_name_base_results + "/Inferred_Graphs/W_Pll_%s_%s_%s.txt" %(file_name_prefix,file_name_ending,str(n_ind))
    tmp = W_inferred
    tmp = tmp/np.linalg.norm(tmp)
    tmp = tmp/(np.abs(tmp).max())
    np.savetxt(file_name,tmp.T,'%2.6f',delimiter='\t')
    #..........................................................................
    
    print 'Inference successfully completed for T = %s ms. The results are saved on %s' %(str(T/1000.0),file_name)
    
    #....................Store Spent Time and Memory............................
    t_end = time.time()                           # The ending time of the algorithm    
    file_name =  file_name_base_results + "/Spent_Resources/CPU_RAM_%s_%s_%s.txt" %(file_name_prefix,file_name_ending,str(n_ind))
    tmp = [T,t_end-t_start,used_ram]
    np.savetxt(file_name,tmp,delimiter='\t')
    #..........................................................................
    
#==============================================================================
