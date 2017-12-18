/* 
   TAMSD.cpp
   Purpose: To calculate the TAMSD from a trajectory of a random walker

   @author: Yousof Mardoukhi
   @version: 1.1 12/12/2017

*/

/*

   Store the calculated value of TAMSD onto an output file
   @params: t The total measurement time
            max_div The number of data points on the interval (0,t)
            run_num The integer number of the run to name a unqiue output file
            latt_num The integer number of the lattice to name a unique output file
            position The position trajectory of random walkers
   @return  an output file named with run_num and latt_num which stores TAMSD for different lag times

*/
//----------------------------TAMSD calculation-----------------------//
void TAMSDLOG(int t, int max_div, int run_num, int latt_num, int **position)
{
	float s;							//A dummy variable to accumulate the infinitesimal increments of the integral
	float dt;							//A dummy variable to store the logarithmic intervals of time
	int lagtime;							//An integer to store the logarithmic intervals of lag time
	char filename[20];						//An array of type char to store the output file
	sprintf(filename,"%s%d%s%d","TAMSD_",latt_num,"_",run_num);	//Assign the file name
	ofstream tamsd;							//Stream the output file
	tamsd.open(filename);						//Open the stream file
	for(int i=0 ; i<max_div ; i++)					//A for loop to go through different lag times
	{
		s = 0;
		dt = 1.0*(i)*(log10(t)-log10(1))/max_div;		//Calculate dt in base 10 logarithm
		lagtime = (int)(pow(10,dt));				//Convert dt into an integer in base 10
		for(int j=0; j<t-lagtime; j++)				//A for loop to integrate
		{
			s = s + pow(position[j+lagtime][0]-position[j][0],2) + pow(position[j+lagtime][1]-position[j][1],2);
		}
		tamsd << s/(float(t-lagtime)) << "\t" << lagtime << endl;
									//Average over the time interval and write the result onto the output file
	}
	tamsd.close();							//Close the stream file
}
//------------------------End of TAMSD calculation---------------------//
