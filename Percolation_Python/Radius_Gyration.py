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
from functools import partial


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
	ind = np.where(X == X[Z[k, 0], Z[k, 1]])
	ind = list(zip(ind[0], ind[1]))
	# save the indices to the output file
	np.save(output, ind)
	# Print the name of the output file
	print(output)


# Defining a function which calculates the radius of gyration of the cluster
# in which the diffusion process happens
def gyration(filename):
	# Change the working directory to the one where the indices of the cluster
	# are stored
	chdir(filepath+'percolation_cluster_indices')
	# Load the files contain the indices for different simulation instances
	ind = np.load(filename)
	# Reshape the array to 2xN where N is the size of cluster
	ind = ind.reshape(np.product(ind.shape)/2, 2)
	print(filename)
	# Calculating the centre of mass along the X and Y-Axis
	x_cm = np.mean(ind[:, 0])
	y_cm = np.mean(ind[:, 1])
	# Calculating the Radius of Gyration along the X and Y-Axis
	r2gx = np.sum((ind[i, 0] - x_cm)**2)
	r2gy = np.sum((ind[i, 1] - y_cm)**2)
	# Calculate the square root of R_2g
	rg = np.sqrt(1.0/len(K)*(r2gx + r2gy))
	# The function returns an expression which shall be later passed to
	# sqlWorkerInsert function to insert the data into the desired database
	return """INSERT INTO gyration (cluster_name, cluster_size, cluster_Rg_x, 
	cluster_Rg_y, cluster_Rg, cluster_xcm, cluster_ycm) 
	VALUES ('%s',%d,%f,%f,%f,%f,%f);""" % (filename, len(ind), np.sqrt(1.0/len(ind)*r2gx),
										   np.sqrt(1.0/len(ind)*r2gy), R_g, x_cm, y_cm)


# Defining a function which insert the output of the function "gyration" to
# store the properties of finite size clusters into a database
def sql_worker_insert(host, user, passwd, db, sql):
	# Make a connection to MySQL server
	# Change the password appropriately
	# The database name in which the data will be stored
	conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
	cursor = conn.cursor()
	# Make the executions to be committed automatically
	cursor.execute("SET AUTOCOMMIT=1")
	# Execute SQL expressions
	cursor.execute(sql)
	cursor.close()
	# Close the connection with MySQL server
	conn.close()


def main(args, N, CPU_n):
	files = []
	for k in range(0, N):
		files.append('indices_%d' % k)
	par_sql_worker = partial(sql_worker_insert, args.host,
							 args.user, args.passwd, args.db)
	
	if args.percolation_identifier:
		# Index of the files which its range is the number of simulations
		index_list = range(0, N)
		# Call the pool method to set the number of processors
		pool = mp.Pool(processes=CPU_n)
		# Extract the percolation clusters indices in a multiprocessing form
		pool.map(percolation_cluster_identifier, index_list)
		# Close pool, join and terminate
		pool.close()
		pool.join()
		pool.terminate()

		# Gather the results from different CPUs and store them in variable 'results'
		sql_expr = pool.map(gyration, files)
		pool.close()
		pool.terminate()

		# Call the map method to perform a parallel computation
		pool.map(par_sql_worker, sql_expr)
		pool.close()
		pool.join()
		pool.terminate()
	else:
		print('Argument was False')
		# Call the pool method to set the number of processors
		pool = mp.Pool(processes=CPU_n)
		# Gather the results from different CPUs and store them in variable 'results'
		sql_expr = pool2.map(gyration, files)
		pool.close()
		pool.terminate()

		# Call the map method to perform a parallel computation
		pool.map(par_sql_worker, sql_expr)
		pool.close()
		pool.join()
		pool.terminate()

	# Change the directory to the root working directory
	chdir(filepath)


if __name__ == '__main__':
	# Initialise a parsing object
	parser = argparse.ArgumentParser(
		description='Choose whether percolation identifier function should be called or not.')
	# Add an optional argument augmented with 'python Radius_Gyration.py'
	# A variable to store the boolean value of the parser
	parser.add_argument('-p', '--percolation-identifier',
						action='store_const', const=True,
						default=False,
						help='Identifies the indices of percolation clusters if used (default is false).')
	parser.add_argument('host', type=str, help="MySQL database server address")
	parser.add_argument('user', type=str, help="database username")
	parser.add_argument('passwd', type=str, help="password for connecting to the database")
	parser.add_argument('db', type=str, help='database name')

	args = parser.parse_args()

	# Number of CPUs to be used for the parallel computing
	CPU_n = mp.cpu_count() - 2
	# Path to the root directory of files
	filepath = input('Please provide the directory path: ')
	# Change to the working directory
	chdir(filepath)

	if args.percolation_identifier:
		# Load the file that contains initial positions of the traces in different simulations
		Z = np.loadtxt('initial_pos')
		# Number of simulations
		N = len(Z) - 1
	else:
		N = input('Please provide the number of clusters to be analysed: ')
	main(args, N, CPU_n)
