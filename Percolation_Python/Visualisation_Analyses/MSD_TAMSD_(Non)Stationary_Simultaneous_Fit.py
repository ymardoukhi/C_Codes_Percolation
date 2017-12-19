import numpy as np									#Importing necessary libraries
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams, ticker
from scipy.optimize import curve_fit, least_squares
from os import chdir
from mpmath import gammainc, inf, gamma, e, exp

fig_size = (16,6)									#Changing the rcParameters for a better figure representation
params = {'backend': 'svg',
          'font.size' : 14,
          'font.weight' : 'normal',
          'axes.labelsize' : 25,
          'axes.linewidth' : 2,
          #'font.weight' : 600,
          #'text.fontsize' : 11,
          'xtick.labelsize' : 22,
          'ytick.labelsize' : 22,
          'figure.figsize': fig_size,
          'xtick.major.pad': 8,
          'ytick.major.pad' :8,
          #'line.markersize' :6,
          'font.family': 'sans-serif',
          'font.sans-serif': 'Liberation Mono',
          'text.latex.preamble' : r'\usepackage{bm}',
          'mathtext.default': 'regular',
          'text.usetex': False}

rcParams.update(params)									#Update the rcParameters

N, MAX_DIV, S, T = 8000, 1000, 793, 400000						#Declare number of trajectories, number of point divisions, cluster size, and time
chdir('path to the working directory')							#Change the working directory

initial_pos = np.loadtxt('initial_pos')							#Load the initial positions of the trajectories
xy_Mass_Centre = np.loadtxt('GyrationRad')						#Load cluster properties such as centre of mass and their radius of gyration (Change to MySQL)

x0 = np.sqrt((initial_pos[0] - xy_Mass_Centre[0])**2 + (initial_pos[1] - xy_Mass_Centre[1])**2)
											#Calculate the distance of the initiial position of trajectories from the centre of mass of the underlying cluster

TAMSD_St = np.loadtxt('TAMSD_FIRST_St')							#Load the data for TAMSD for the stationary case
TAMSD_St_y = TAMSD_St[:,1]
TAMSD_St_x = TAMSD_St[:,0]

MSD_St = np.loadtxt('MSD_St')								#Load the data for MSD for the stationary case
MSD_St_y = MSD_St[:,1]
MSD_St_x = MSD_St[:,0]

TAMSD = np.loadtxt('TAMSD_FIRST_0')							#Load the data for TAMSD for the fixed initial position case
TAMSD_y = TAMSD[:,1]
TAMSD_x = TAMSD[:,0]

MSD = np.loadtxt('MSD_0')								#Load the data for MSD for the fixed initial position case
MSD_y = MSD[:,1]
MSD_x = MSD[:,0]

##########################################################
# Definine a fitting curve function with fitting parame- #
# ters D, h, df, dw, standing on the diffusion constant, #
# equality constant for the equality between the radius  #
# of gyration and clusters' size, fractal dimension and  #
# random walk dimension.                                 #
##########################################################
def fitting_curve(x, D, h, df, dw):
	result = np.zeros((len(x)))
	for i in range(0,len(x)):
		result[i] = 2*(h**2)*(S**(2/df))*(1-float(exp(-D/(2*(h**2))*(x[i]**(2/dw))/(S**(2/df)))))
	return result
##########################################################
# Definine a cost function to estimate the values for D, #
# h, df and dw                                           #
##########################################################
def residual_fun(params, x_data, y_data):
	D, h, df, dw = params[0], params[1], params[2], params[3]
	diff = y_data - fitting_curve(x_data, D, h, df, dw)				#The residual value (cost function) between data values and the fitting curve's value
	return diff
##########################################################
# Define a fitting curve for MSD in the case of non-sta- #
# tionary setup.				         #
##########################################################
def fitting_curve_MSD(x, D, h, df, dw):
	result = np.zeros((len(x)))
	for i in range(0,len(x)):
		result[i] = (x0**2)*(1 - float(exp(-D/(2*(h**2))*(x[i]**(2/dw))/(S**(2/df)))))**2 + (h**2)*(S**(2/df))*(1-float(exp(-2*D/(2*(h**2))*(x[i]**(2/dw))/(S**(2/df)))))
	return result
##########################################################
# Define a fitting curve for TAMSD in the case of non-   #
# stationary setup.				         #
##########################################################
def fitting_curve_TAMSD(x, D, h, df, dw):
	result = np.zeros((len(x)))
	for i in range(0,len(x)):
		result[i] =  2*(h**2)*(S**(2/df))*(1-float(exp(-D/(2*(h**2))*(x[i]**(2/dw))/(S**(2/df))))) + (x0**2 - (h**2)*(S**(2/df)))*((1 - float(exp(-D/(2*(h**2))*(x[i]**(2/dw))/(S**(2/df)))))**2)*((1-float(exp(-D/((h**2))*((T-x[i])**(2/dw))/(S**(2/df)))))/(D/(h**2)*((T-x[i])**(2/dw))/(S**(2/df))))
	return result
##########################################################
# Define a cost function to estimate the values for D,   #
# h, df and dw for MSD and TAMSD curves simultaneously.  #
##########################################################
def residual_fun_Simultaneous(params, x_data1, y_data1, x_data2, y_data2):
	D, h, df, dw = params[0], params[1], params[2], params[3]
	diff1 = y_data1 - fitting_curve_MSD(x_data1, D, h, df, dw)			#The cost function for non-stationary MSD
	diff2 = y_data2 - fitting_curve_TAMSD(x_data2, D, h, df, dw)			#The cost function for non-stationary TAMSD
	return np.concatenate((diff1, diff2))						#Concatenate the cost functions for MSD and TAMSD
##########################################################

par_initial=[1.0, 1.0, 1.5, 2.6]
res_val_TAMSD_St = least_squares(residual_fun, par_initial, bounds=([0, 0, 1, 2], [5, 5, 2, 3]), loss='cauchy', args=(TAMSD_St_x, TAMSD_St_y))
res_val_MSD_St = least_squares(residual_fun, par_initial, bounds=([0, 0, 1, 2], [5, 5, 2, 3]), loss='cauchy', args=(MSD_St_x, MSD_St_y))

res_val_Simul = least_squares(residual_fun_Simultaneous, par_initial, bounds=([0, 0, 1, 2], [5, 5, 2, 3]), loss='cauchy', args=(MSD_x, MSD_y, TAMSD_x, TAMSD_y))

ax1 = plt.subplot(122)
ax1.plot(MSD_St_x[0::10000], MSD_St_y[0::10000], marker='^', linestyle='None', markersize= 8, color='k', label='MSD Simulation')
ax1.plot(TAMSD_St_x[0::10], TAMSD_St_y[0::10], marker='s', linestyle='None', markersize=6, color='k', markerfacecolor='white', label='TAMSD Simulation')
ax1.plot(MSD_St_x, fitting_curve(MSD_St_x, *res_val_MSD_St.x), linestyle='--', color='k', label='MSD & TAMSD Analytics')
ax1.xaxis.get_major_formatter().set_powerlimits((0, 1))
ax1.yaxis.get_major_formatter().set_powerlimits((0, 1))
ax1.set_xlabel(r'$t, \Delta$')
plt.legend()

ax2 = plt.subplot(121)
ax2.plot(MSD_x[0::10000], MSD_y[0::10000], marker='^', linestyle='None', markersize= 8, color='k', label='MSD Simulation')
ax2.plot(TAMSD_x[0::10], TAMSD_y[0::10], marker='s', linestyle='None', markersize=6, color='k', markerfacecolor='white', label='TAMSD Simulation')
ax2.plot(TAMSD_x[len(TAMSD_x)-1], TAMSD_y[len(TAMSD_x)-1], marker='s', linestyle='None', markersize=6, color='k', markerfacecolor='white')
ax2.plot(MSD_x, fitting_curve_MSD(MSD_x, *res_val_MSD_St.x), linestyle='--', color='k', label='MSD Analytics')
ax2.plot(TAMSD_x, fitting_curve_TAMSD(TAMSD_x, *res_val_MSD_St.x), linestyle='-.', color='k', label='TAMSD Analytics')
ax2.xaxis.get_major_formatter().set_powerlimits((0, 1))
ax2.yaxis.get_major_formatter().set_powerlimits((0, 1))
ax2.set_ylabel(r'$\left\langle \mathbf{r}^2_{\mathcal{C}}(t) \right\rangle, \left\langle \overline{\delta^2_{\mathcal{C}}}(\Delta) \right\rangle$')
ax2.set_xlabel(r'$t, \Delta$')
ax2.annotate(r'$R_g^2$', xy=(200000,500), xytext=(200000,500))

plt.legend()
plt.show()
