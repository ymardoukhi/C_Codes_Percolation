#########################################################
#    A python code to extract the indices of a cluster  #
#    which the diffusion of the particle happens within #
#    and calculate the radius of gyration of this very	#
#    cluster, as well as their centre of mass and store #
#    them in a database by the means of MySQL		#
#########################################################
#		@author: Yousof Mardoukhi		#
#		@version: 1.1 14.12.2017		#
#########################################################

import multiprocessing as mp				#Import necessary libraries
import numpy as np
from os import chdir
import MySQLdb
import argparse

parser = argparse.ArgumentParser(description='Choose whether percolation identifier function should be called or not.')
							#Initialise a parsing object
parser.add_argument('-p', '--percolation-identifier', action='store_const', const=True, default=False, help='Identifies the indices of percolation clusters if used (default is false).')
							#Add an optional argument augumented with 'python Radius_Gyration.py'
args = parser.parse_args()				#A variable to store the boolean value of the parser


CPU_n = mp.cpu_count()-2				#Number of CPUs to be used for the parallel computing
filepath = input('Please give the directory path: ')	#Path to the root directory of files
chdir(filepath)						#Change to the working directory

if args.percolation_identifier == True:
	Z = np.loadtxt('initial_pos')			#Load the file that contains initial positions of the traces in different simulations
	N = len(Z)-1					#Number of simulations
else:
	N = input('Please provide the number of clusters to be analysed: ')



####################################################################################################################
####################################################################################################################
#Defining a function which extract the indices of the percolation cluster
def percolation_culster_identifier(k):
	inputfile = 'label_%d' %(k)			#The input file is a file contains inforamtion about the labels of different cluster
	output = 'indices_%d'  %(k)			#Naming the output file, it simply contains information about the indices of the cluster
	chdir(filepath+'labelboard')			#Change directory to the one contains the labelling boards
	X = np.loadtxt(inputfile)			#Load the labelled board
	chdir(filepath+'percolation_cluster_indices')	#Change the directory to the one where the output files are stored
	index_file = open(output, 'w')			#Open a stream file for the purpose of writing on output files

	for i in range(0,len(X)):			#A for loop goes through all the cells of the label board and catch those having the same index as the staring point of the diffusion process
		for j in range(0,len(X)):
			if (X[i,j] == X[Z[k,0],Z[k,1]]):
				index_file.write(str(i) + '\t' + str(j) + '\n')
	index_file.close()				#Close the output file
	print(output)					#Print the name of the output file

####################################################################################################################
####################################################################################################################
#Defining a function which calculates the radius of gyration of the cluster in which the diffusion process happens
def gyration(filename):
	chdir(filepath+'percolation_cluster_indices')	#Change the working directory to the one where the indices of the cluster are stored
	K = np.loadtxt(filename)			#Load the files contain the indices for different simulation instances
	K = K.reshape(np.product(K.shape)/2,2)		#Reshape the array to 2xN where N is the size of cluster
	print(filename)
	R_2_g_x = 0					#Initiating a variable which stores the square of the radius of gyration x-component
	R_2_g_y = 0					#Initiating a variable which stores the square of the radius of gyration y-component
	x_cm = np.sum(K[:,0])/len(K)			#Centre of mass along the x-axis
	y_cm = np.sum(K[:,1])/len(K)			#Centre of mass along the y-axis
	for i in range(0, len(K)):			#A for loop to calculate the radius of gyration
		R_2_g_x = R_2_g_x + (K[i, 0] - x_cm)**2  
		R_2_g_y = R_2_g_y + (K[i, 1] - y_cm)**2
	R_g = np.sqrt(1.0/len(K)*(R_2_g_x + R_2_g_y))	#Calculate the square root of R_g_2
	return """INSERT INTO gyration (cluster_name, cluster_size, cluster_Rg_x, cluster_Rg_y, cluster_Rg, cluster_xcm, cluster_ycm) VALUES ('%s',%d,%f,%f,%f,%f,%f);""" %(filename, len(K), np.sqrt(1.0/len(K)*R_2_g_x), np.sqrt(1.0/len(K)*R_2_g_y), R_g, x_cm, y_cm)
							#The function returns an expression which shall be later passed to sqlWorkerInsert function to insert the data into the desired database
####################################################################################################################
####################################################################################################################
#Defining a function which insert the output of the function "gyration" to store the properties of finite size clusters into a database
def sqlWorkerInsert(sql):
	conn = MySQLdb.connect(host = "127.0.0.1",	#Make a connection to MySQL server
		user = "yousof",
		passwd = "password",			#Change the password appropriately
		db = "GyrationRadius")			#The database name in which the data will be stored
	cursor = conn.cursor()
	cursor.execute("SET AUTOCOMMIT=1")		#Make the executions to be committed automatically
	cursor.execute(sql)				#Execute SQL expressions
	cursor.close()
	conn.close()					#Close the connection with MySQL server
####################################################################################################################
####################################################################################################################
def main(args, N, CPU_n):
	files = []
	for k in range(0,N):
		files.append('indices_%d' %(k))
	

	if args.percolation_identifier == True:
		index_list = range(0,N)			#Index of the files which its range is the number of simulations
		pool1 = mp.Pool(processes=CPU_n)	#Call the pool method to set the number of processors
		pool1.map(percolation_cluster_identifier, index_list)
							#Extract the percolation clusters indices in a multiprocessing form
		pool1.close()				#Close pool1
		pool1.join()				#Concatenate the result
		pool1.terminate()			#Terminate pool1

		pool2 = mp.Pool(processes=CPU_n)	#Call the pool method to set the number of processors
		sql_expr = pool2.map(gyration, files)	#Gather the results from different CPUs and store them in variable 'results'
		pool2.close()
		pool2.terminate()			#Terminate pool2
	
		pool3 = mp.Pool(processes=CPU_n)	#Call the poo3 method to set the number of processors
		pool3.map(sqlWorkerInsert, sql_expr)	#Call the map method to perform a parallel computation
		pool3.close()
		pool3.join()
		pool3.terminate()			#Terminate pool3
	else:
		print('Argument was False')
		pool2 = mp.Pool(processes=CPU_n)	#Call the pool method to set the number of processors
		sql_expr = pool2.map(gyration, files)	#Gather the results from different CPUs and store them in variable 'results'
		pool2.close()
		pool2.terminate()			#Terminate pool2
	
		pool3 = mp.Pool(processes=CPU_n)	#Call the pool method to set the number of processors
		pool3.map(sqlWorkerInsert, sql_expr)	#Call the map method to perform a parallel computation
		pool3.close()
		pool3.join()
		pool3.terminate()			#Terminate pool1
	
	chdir(filepath)					#Change the directory to the root working directory
####################################################################################################################
####################################################################################################################
if __name__ == '__main__':
	main(args, N, CPU_n)
