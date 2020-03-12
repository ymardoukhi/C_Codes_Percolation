#########################################################
#    A python code to extract the indices of a cluster  #
#    which the diffusion of the particle happens within #
#    and calculate the radius of gyration of this very	#
#    cluster, as well as their centre of mass and store #
#    them in a database by the means of MySQL library   #
#########################################################
#		@author: Yousof Mardoukhi		#
#		@version: 1.1 14.12.2017		#
#########################################################
# Import necessary libraries
import multiprocessing as mp
import numpy as np
from os import chdir
import MySQLdb
import argparse

# Initialise a parsing object
parser = argparse.ArgumentParser(description='Choose whether percolation identifier function should be called or not.')
# Add an optional argument augmented with 'python Radius_Gyration.py'
# A variable to store the boolean value of the parser
parser.add_argument('-p', '--percolation-identifier',
					action='store_const', const=True,
					default=False, help='Identifies the indices of percolation clusters if used (default is false).')

args = parser.parse_args()

# Number of CPUs to be used for the parallel computing
CPU_n = mp.cpu_count()-2
# Path to the root directory of files
filepath = input('Please provide the directory path: ')
# Change to the working directory
chdir(filepath)

if args.percolation_identifier:
	# Load the file that contains initial positions of the traces in different simulations
	Z = np.loadtxt('initial_pos')
	# Number of simulations
	N = len(Z)-1
else:
	N = input('Please provide the number of clusters to be analysed: ')


# Defining a function which extract the indices of the percolation cluster
def percolation_culster_identifier(k):
	# The input file is a file contains which information about the labels of different cluster
	inputfile = 'label_%d' % k
	# Naming the output file, it simply contains information about the indices of the cluster
	output = 'indices_%d' % k
	# Change directory to the one contains the labelling boards
	chdir(filepath+'labelboard')
	# Load the labelled board
	X = np.loadtxt(inputfile)
	# Change the directory to the one where the output files are stored
	chdir(filepath+'percolation_cluster_indices')
	# Open a stream file for the purpose of writing on output files
	index_file = open(output, 'w')

	# Find the indices where the the label mathechs the initial label
        # of the input file
        ind = np.where(X == X[Z[k, 0], Z[k, 1]]
        ind = list(zip(ind[0], ind[1]))
        # save the indices to the output file
        np.save(output, ind)
	# Print the name of the output file
	print(output)

#Defining a function which calculates the radius of gyration of the cluster 
# in which the diffusion process happens
def gyration(filename):
        #Change the working directory to the one where the indices of the cluster 
        # are stored
	chdir(filepath+'percolation_cluster_indices')	
        #Load the files contain the indices for different simulation instances
	K = np.load(filename)			
        #Reshape the array to 2xN where N is the size of cluster
	K = K.reshape(np.product(K.shape)/2,2)		
	print(filename)
        # Calculating the centre of mass along the X and Y-Axis
	x_cm = np.mean(K[:,0])			
	y_cm = np.mean(K[:,1])			
        # Calculating the Radius of Gyration along the X and Y-Axis
	R_2gX = np.sum((K[i, 0] - x_cm)**2)
	R_2gY = np.sum((K[i, 1] - y_cm)**2)
        #Calculate the square root of R_2g
	R_g = np.sqrt(1.0/len(K)*(R_2gX + R_2gY))	
        # The function returns an expression which shall be later passed to 
        # sqlWorkerInsert function to insert the data into the desired database
	return """INSERT INTO gyration (cluster_name, cluster_size, cluster_Rg_x, 
                  cluster_Rg_y, cluster_Rg, cluster_xcm, cluster_ycm) 
                  VALUES ('%s',%d,%f,%f,%f,%f,%f);""" %(filename, len(K), 
                      np.sqrt(1.0/len(K)*R_2gX), np.sqrt(1.0/len(K)*R_2gY), R_g, x_cm, y_cm)

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
