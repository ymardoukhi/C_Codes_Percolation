//-----------------------------MSD calculation------------------------//
float *MSD(int t, int n, int **position)
{
	float *R2 = new float[t];											//Defining the variable R for calculating the MSD

	
	for (int i=0 ; i<t ; i++)											//time for loop
	{
		R2[i] =  pow(position[i][0]-position[0][0],2)+pow(position[i][1]-position[0][1],2);
	}
	
	return R2;
}
//-------------------------End of MSD calculation---------------------//
