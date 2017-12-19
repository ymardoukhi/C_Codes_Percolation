#include <iostream>
#include <time.h>
#include <fstream>
#include <math.h>

using namespace std;
long idum1 = -time(NULL);

#include "headers/ran1.h"
#include "headers/MSD.h"
#include "headers/TAMSD.h"
#include "headers/Sq_Latt_RW.h"
#include "headers/board_init.h"
//------------------------------------------------------------//
int main()
{
	int n,t,size,latt_num,max_div; float p; char ilabel;					//Initiating the necessary variables, number of runs, total time, lattice size, number of generated lattice, percolation density and dommy char variable respectively.
	
	FILE *ifp;										//File variable ifp
	ifp=fopen("inputs.txt","r");								//Openning the input file for reading the variables
	fscanf(ifp,"%s %d\n",&ilabel,&n);							//Reading the first line, number of runs
	fscanf(ifp,"%s %d\n",&ilabel,&t);							//Reading the second line, total time
	fscanf(ifp,"%s %d\n",&ilabel,&size);							//Reading the third line, lattice size
	fscanf(ifp,"%s %d\n",&ilabel,&latt_num);						//Reading the fourth line, number of generated lattices
	fscanf(ifp,"%s %d\n",&ilabel,&max_div);
	fscanf(ifp,"%s %f\n",&ilabel,&p);							//Reading the fifth line, percolation density
	printf("Sample #N(%d) t(%d) size(%d) p(%f) number_of_lattice(%d) tamsd_division(%d)\n",n,t,size,p,latt_num,max_div);
												//Run-time on screen print of the variables
	fclose(ifp);										//Close the read-file ifp

	ofstream msd;										//Initiating msd stream variable for writing final MSD on it.
	msd.open("MSD.txt");									//Openning the MSD.txt file for streaming R variable

	float *R_latt = (float*) calloc (t, sizeof(float));					//A pointer to store the geometry averaged MSD
	for (int i=0; i<latt_num ; i++)								//A for-loop runs over different lattices with the same percolation density
	{
		int **board = lattice_geometry(p, size, i);					//Storing the geometry of the lattice onto variable board by calling function lattice_geometry
		cout << "Number #" << i << endl;

		float *R = (float*) calloc (t, sizeof(float));					//Temporary pointer 'R' which will be used for averageing over different run for different lattices with the same percolation density
		
		for (int k=0; k<n; k++)
		{
			cout << "Number of run" << k << endl;
			int **position = random_walk(t, k, size, board, i);			//Call the random_walk function to simulate a random walk process
			if(k<11) TAMSDLOG(t, max_div, k, i, position);				//Call the TAMSDLOG function to store TAMSD data onto an output file
			float *R2 = MSD(t, k, position);					//Storing the radius vector of each run onto variable R2 by calling the diffusion process function
			for (int i=0; i<t ; i++)
			{
				delete[] position[i];
			}
			delete[] position;
			for (int j=0; j<t ; j++)						//A for-loop for setting array R to zero
			{
				R[j] = R[j] + R2[j];
			}
			delete[] R2;
		}
		for (int j=0; j<t ; j++)							//A for-loop for setting array R to zero
		{
			R[j] = R[j]/(1.0*float(n));
			R_latt[j] = R_latt[j] + R[j];											
		}
		for (int k=0; k<size; k++)
		{
			 free(board[k]);
		}
		free(board);
		free(R);
	}
	for (int j=0 ; j<t ; j++)								//A for loop for averageing the elements of R
	{
		R_latt[j] = R_latt[j]/(1.0*float(latt_num));					//Averageing R for different lattices
		msd << R_latt[j] << endl;							//Streaming R variable on msd stream file MSD.txt
	}
	free(R_latt);
	msd.close();										//Closing the stream file MSD.txt
	return 0;
}
