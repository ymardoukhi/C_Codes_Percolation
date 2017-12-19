//------------------------TAMSD at specific lagtime--------------------//
float TAMSD_SCATT(int t, int **position, int lagtime)
{
	float s=0;
	for(int i = 0; i<t-lagtime; i++)
	{
		s = s + pow(position[i+lagtime][0]-position[i][0],2) + pow(position[i+lagtime][1]-position[i][1],2);
	}
	s = s/(float(t-lagtime));
	return s;
}
//-------------------End of TMASD at specific lagtime------------------//
