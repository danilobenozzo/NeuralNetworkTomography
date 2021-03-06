#=======================IMPORT THE NECESSARY LIBRARIES=========================
import numpy as np
import sys,getopt,os
import matplotlib.pyplot as plt
from scipy.cluster.vq import whiten
import matplotlib.mlab as mlab

try: 
    import plotly.plotly as pltly
    from plotly.graph_objs import *
    plotly_import = 1
except:
    print 'Plotly was not found. No problem though, life goes on ;)'
    plotly_import = 0

os.chdir('../')
sys.path.append('./')


from CommonFunctions.Neurons_and_Networks import *
from CommonFunctions.default_values import *
from CommonFunctions.auxiliary_functions_digitize import parse_commands_ternary_algo,beliefs_to_ternary
from CommonFunctions.auxiliary_functions import generate_file_name,combine_weight_matrix
from CommonFunctions.auxiliary_functions_plot import export_to_plotly

os.system('clear')                                              # Clear the commandline window
#==============================================================================

#==========================PARSE COMMAND LINE ARGUMENTS========================
input_opts, args = getopt.getopt(sys.argv[1:],"hE:I:P:Q:T:S:D:A:F:R:L:M:B:R:G:J:K:U:Z:Y:O:f:")
frac_stimulated_neurons,T_max,ensemble_size,file_name_base_data,ensemble_count_init,generate_data_mode,ternary_mode,file_name_base_results,inference_method,sparsity_flag,we_know_topology,beta,alpha0,infer_itr_max,T_range,plot_flags = parse_commands_ternary_algo(input_opts)
#==============================================================================

#================================INITIALIZATIONS===============================

#--------------------------Initialize the Network------------------------------
Network = NeuralNet(None,None,None,None,None,None,None, 'command_line',input_opts,args)
#------------------------------------------------------------------------------    


#-----------------------------Signin to Plotly---------------------------------
plotly_flag = 0                     # If '1', figures will be exported to PlotLy (https://plot.ly/) as well
if not plotly_import:               # If PlotLy was not installed, there is no need to consider its plottings
    plotly_flag = 0
    
if plotly_flag:
    usrname = raw_input("What is your PlotLy username? ")
    passwd = raw_input("What is your PlotLy API Key? ")
    if not passwd:
        passwd = 'wj370nzaqg'
    pltly.sign_in(usrname, passwd)
#------------------------------------------------------------------------------

#==============================================================================

#=============================READ THE RESULTS=================================

#----------------------------Get the Actual Graph------------------------------
Network.read_weights(0,file_name_base_data)
W,DD_tot = combine_weight_matrix(Network)
#------------------------------------------------------------------------------

#--------------------Get the Inferred Graph for NeuInf-------------------------
T = T_range[0]
file_name_ending = generate_file_name(Network.file_name_ending,3,we_know_topology,'A',generate_data_mode,infer_itr_max,frac_stimulated_neurons,sparsity_flag,T,'N')
file_name = file_name_base_results + "/Inferred_Graphs/W_%s.txt" %file_name_ending
try:
    W_inferred_neuinf = np.genfromtxt(file_name, dtype=None, delimiter='\t')
    n,m = W.shape
    W_inferred_neuinf = W_inferred_neuinf[:,0:m]
    W_inferred_neuinf = W_inferred_neuinf + np.random.rand(n,m)/100000
    W_inferred_neuinf  = whiten(W_inferred_neuinf)
    found_file_tot = 1
except:
    found_file_tot = 0
    print 'Sorry I can not find the corresponding inference file for NeuInf'
#------------------------------------------------------------------------------

#----------------------Get the Inferred Graph for GLM--------------------------
T = T_range[1]
file_name_ending = generate_file_name(Network.file_name_ending,8,we_know_topology,'A',generate_data_mode,infer_itr_max,frac_stimulated_neurons,sparsity_flag,T,'N')
file_name = file_name_base_results + "/Inferred_Graphs/W_%s.txt" %file_name_ending
try:
    W_inferred_glm = np.genfromtxt(file_name, dtype=None, delimiter='\t')
    n,m = W.shape
    W_inferred_glm = W_inferred_glm[:,0:m]
    W_inferred_glm = W_inferred_glm + np.random.rand(n,m)/100000
    W_inferred_glm  = whiten(W_inferred_glm)
    found_file_glm = 1
except:
    found_file_glm = 0
    print 'Sorry I can not find the corresponding inference file for GLM'
#------------------------------------------------------------------------------

#==============================================================================



#=================================PLOT THE RESULTS=============================
fig, axs = plt.subplots(nrows=1, ncols=2)
if (found_file_tot):
    ax = axs[0]
    ax.scatter(np.sign(W.ravel()),W_inferred_neuinf.ravel())
    ax.set_title('Stochastic NeuInf')
    ax.set_xlabel('G (actual)', fontsize=16)
    ax.set_ylabel('W (inferred)', fontsize=16)

if found_file_glm:
    ax = axs[1]
    ax.scatter(np.sign(W.ravel()),W_inferred_glm.ravel())
    ax.set_title('GLM')
    ax.set_xlabel('G (actual)', fontsize=16)
    ax.set_ylabel('W (inferred)', fontsize=16)

plt.show();
#==============================================================================

