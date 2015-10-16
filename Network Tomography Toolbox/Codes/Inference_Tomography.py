#=======================IMPORT THE NECESSARY LIBRARIES=========================
from time import time
import numpy as np
import sys,getopt,os
import matplotlib.pyplot as plt
import pdb
from copy import deepcopy
from scipy.cluster.vq import whiten
from scipy.signal import find_peaks_cwt

from CommonFunctions.auxiliary_functions import read_spikes,combine_weight_matrix,combine_spikes_matrix,generate_file_name,spike_binning
from CommonFunctions.auxiliary_functions_inference import *
from CommonFunctions.Neurons_and_Networks import *

#from sklearn import metrics

os.system('clear')                                              # Clear the commandline window
#==============================================================================

#==========================PARSE COMMAND LINE ARGUMENTS========================
input_opts, args = getopt.getopt(sys.argv[1:],"hE:I:P:Q:T:S:D:A:F:R:L:M:B:X:Y:C:V:J:U:Z:b:p:j:o:")

frac_stimulated_neurons,no_stimul_rounds,ensemble_size,file_name_base_data,ensemble_count_init,generate_data_mode,file_name_base_results,inference_method,sparsity_flag,we_know_topology,verify_flag,beta,alpha0,infer_itr_max,p_miss,jitt,bin_size,neuron_range = parse_commands_inf_algo(input_opts)
#==============================================================================


#================================INITIALIZATIONS===============================

#---------------------Initialize Simulation Variables--------------------------
theta = 5.005                                               # The update threshold of the neurons in the network
d_window = 10                                           # The time window the algorithm considers to account for pre-synaptic spikes
sparse_thr0 = 0.15                                    # The initial sparsity soft-threshold (not relevant in this version)
max_itr_optimization = 2250                              # This is the maximum number of iterations performed by internal optimization algorithm for inference    
#------------------------------------------------------------------------------

#-------------------------Initialize Inference Parameters----------------------
inference_method = 7
sparsity_flag = 5
#...........................SOTCHASTIC NEUINF Approach.........................
if (inference_method == 3) or (inference_method == 2):        
    beta = 10
    inferece_params = [alpha0,sparse_thr0,sparsity_flag,theta,max_itr_optimization,d_window,beta,bin_size]
#..............................................................................

#...........................Cross Correlogram Approach.........................
elif (inference_method == 4):
    d_window = 15                                           # The time window the algorithm considers to compare shifted versions of two spiking patterns
    inferece_params = [d_window]            
#..............................................................................

#.................................MSE-based Approach...........................
if (inference_method == 7):    
    inferece_params = [alpha0,sparse_thr0,sparsity_flag,theta,max_itr_optimization,d_window,beta,bin_size]
#..............................................................................

#------------------------------------------------------------------------------

#==============================================================================


#===============================READ THE SPIKES================================
    
#----------------------------Read and Sort Spikes------------------------------
#file_name = '../Data/Spikes/fluorescence_mocktest_adapted.txt'
file_name = '../Data/Spikes/Spike_Times2.txt'
#file_name = '../Data/Spikes/HC3_ec013_198_processed.txt'
#file_name = '../Data/Spikes/Spikes_exc.txt'
#file_name = '../Data/Spikes/Moritz_Spike_Times_Reduced.txt'
Neural_Spikes,T_max = read_spikes(file_name)
#------------------------------------------------------------------------------
    
#--------Calculate the Range to Assess the Effect of Recording Duration--------
T_max = int(1000*T_max)
T_step = int(T_max/6.0)
T_range = range(T_step, T_max+1, T_step)
print T_range

T_range = [T_max]
#------------------------------------------------------------------------------
    
#==============================================================================

#====================READ THE GROUND TRUTH IF POSSIBLE=========================
#file_name = '../Data/Graphs/network_mocktest_adapted.txt'
file_name = '../Data/Graphs/Connectivity_Matrix2.txt'
#file_name = '../Data/Graphs/Matrix_Accurate.txt'
#file_name = '../Data/Graphs/Moritz_Actual_Connectivity.txt'
W_act = np.genfromtxt(file_name, dtype=None, delimiter='\t')
n,m = W_act.shape
#file_name = '../Data/Graphs/Delay_Matrix2.txt'
#D_act = np.genfromtxt(file_name, dtype=None, delimiter='\t')
#DD_act = np.multiply(np.sign(abs(W_act)),D_act)
#==============================================================================

#============================INFER THE CONNECTIONS=============================
       
#--------------------------Infer the Graph For Each T--------------------------
for T in T_range:
        
    #.......................Assign Inference Parameters........................
    if p_miss or jitt:
        
        for itr in range(0,10):
            if p_miss:
                out_spikes_tot_mat_orig,out_spikes_tot_nonzero,non_zero_neurons = combine_spikes_matrix(Neural_Spikes,T,jitt,int(1/p_miss))
            else:
                out_spikes_tot_mat_orig,out_spikes_tot_nonzero,non_zero_neurons = combine_spikes_matrix(Neural_Spikes,T,jitt,0)
        
            if bin_size:    
                #out_spikes_tot = spike_binning(out_spikes_tot_mat_orig,bin_size)
                out_spikes_tot_mat = spike_binning(out_spikes_tot_nonzero,bin_size)
            else:
                out_spikes_tot_mat = out_spikes_tot_mat_orig
        
            n = max(non_zero_neurons) + 1
            m = n
            W_estimated = np.zeros([n,m])    
            fixed_entries = np.zeros([n,m])
            #..........................................................................
        
            #............................Perfrom Inference.............................
        
            #-------------------Perform the Inference Step----------------
            W_temp,cost,Inf_Delays = inference_alg_per_layer(out_spikes_tot_mat,out_spikes_tot_mat,inference_method,inferece_params,W_estimated,0,'R',neuron_range)
            
            if itr == 0:
                W_inferred = W_temp
            else:
                W_inferred = W_inferred + W_temp
            #-------------------------------------------------------------
        
        W_inferred = np.divide(W_inferred,float(itr+1))
        
    else:
        out_spikes_tot_mat_orig,out_spikes_tot_nonzero,non_zero_neurons = combine_spikes_matrix(Neural_Spikes,T,0,0)
        if bin_size:
            #out_spikes_tot = spike_binning(out_spikes_tot_mat_orig,bin_size)
            out_spikes_tot_mat = spike_binning(out_spikes_tot_nonzero,bin_size)
        else:
            out_spikes_tot_mat = out_spikes_tot_mat_orig[:,0:T]
            #V = np.zeros([n,T])
            #for jj in range(0,T-1):
            #    V[:,jj] = np.sum(out_spikes_tot_mat[:,max(0,jj-d_window):jj],axis = 1)
        
        n = max(non_zero_neurons) + 1
        m = n
        W_estimated = np.zeros([n,m])    
        fixed_entries = np.zeros([n,m])
            
        #W_inferred,cost,Inf_Delays = inference_alg_per_layer(out_spikes_tot_mat,out_spikes_tot_mat,inference_method,inferece_params,W_estimated,0,'R',neuron_range)
        W_inferred,Inf_Delays = delayed_inference_constraints(out_spikes_tot_mat,d_window,max_itr_optimization,sparse_thr0,theta,[],[],neuron_range)
        
    #--------------Post-Process the Inferred Matrix---------------
    if len(non_zero_neurons) != n:
        m,c = W_inferred.shape
        W = np.zeros([n,m])
        itr = 0
        for i in range(0,n):
            if i in non_zero_neurons:
                W[i,:] = W_inferred[itr,:]
                itr = itr + 1
            
        W_inferred = np.zeros([n,n])
        itr = 0
        for i in range(0,n):            
            if i in non_zero_neurons:
                W_inferred[:,i] = W[:,itr]
                itr = itr + 1
                    
            W_inferred[i,i] = 0
    
    W_inferred = np.array(W_inferred)        
    #WW = W_inferred + np.random.rand(n,n)/1000000000.0
    WW = whiten(W_inferred)
    
    #W_region = np.zeros([n,n])
    #for i in range(0,n):
    #    for j in range(i,n):
    #        #W_region[i,j] = (W_deg[i,6]+1) * (W_deg[j,6]+1)
    #        W_region[i,j] = W_deg[i,6] - W_deg[j,6]
    #        W_region[j,i] = W_region[i,j]
    #        
    #plt.subplot(1,2,1);plt.imshow(WW);plt.subplot(1,2,2);plt.imshow(W_region);plt.show()
    #plt.subplot(1,2,1);plt.imshow(np.log(Inf_Delays));plt.subplot(1,2,2);plt.imshow(np.multiply(abs(np.sign(W_act)),D_act));plt.show()
    #plt.plot(np.log(0.000001+Inf_Delays[1,:]));plt.plot(1000*DD_act[1,:],'r');plt.show()
    #-------------------------------------------------------------
        
        
    #..........................................................................
        
    #.........................Save the Belief Matrices.........................
    file_name_ending = 'I_' + str(inference_method) + '_S_' + str(sparsity_flag) + '_T_' + str(T)
    if p_miss:
        file_name_ending = file_name_ending + '_pM_' + str(p_miss)
    if jitt:
        file_name_ending = file_name_ending + '_jt_' + str(jitt)
    if bin_size:
        file_name_ending = file_name_ending + '_bS_' + str(bin_size)
        
    
    if len(neuron_range) == 0:
        file_name =  file_name_base_results + "/Inferred_Graphs/W_%s.txt" %file_name_ending
        np.savetxt(file_name,WW,'%2.5f',delimiter='\t')
    else:        
        for ik in neuron_range:
            file_name =  file_name_base_results + "/Inferred_Graphs/W_Pll_%s_%s.txt" %(file_name_ending,str(ik))
            np.savetxt(file_name,WW[:,ik].T,'%2.5f',delimiter='\t')

    #..........................................................................
    
    print 'Inference successfully completed for T = %s ms' %str(T/1000.0)    
    #----------------------------------------------------------------------


    #--------------------------Calculate Accuracy-------------------------
    #WW = (W>0).astype(int)
    #fpr, tpr, thresholds = metrics.roc_curve(WW.ravel(),whiten(W_inferred).ravel())    
    #print('\n==> AUC = '+ str(metrics.auc(fpr,tpr))+'\n');
    #----------------------------------------------------------------------
    
    
#for i in range(0,n):
#    W_inferred[i,i] = 0
#plt.subplot(1,2,1);plt.imshow(whiten(W_inferred));plt.subplot(1,2,2);plt.imshow(np.sign(W));plt.show()
#pdb.set_trace()
#plt.plot(fpr,tpr)



#--------------Evaluate Quality of Delay Estimation----------------
if 0 :
    tau_m = 10.0
    DD = np.log(1e-10 + abs(Inf_Delays))
    #DD = abs(Inf_Delays)/(.6)
    DD = np.multiply(DD,(DD>0).astype(int))
    #DD = DD*tau_m
    #plt.plot(DD[1,:]);plt.plot(1000*DD_act[1,:],'r');plt.show()
    AA = np.sum(np.multiply((DD>0),(DD_act)>0))
    rec = AA/float(sum(DD_act>0))
    prec = AA/float(sum(DD>0))
    dist = np.linalg.norm(DD-DD_act)


    W_act2 = W_act
    for i in range(0,n):
        W_act2[i,i] = -0.002