//----------------------Board function----------------//
int **lattice_geometry(float p, int size, int latt_num)
{
	ofstream board_file;							//Streaming of board of percolation
	char filename[10];
	sprintf(filename,"%s%d","board",latt_num);
	board_file.open(filename);						//Open a text file "board" for streaming the percolated space
	int i, j;								//Indices count for the lattice size

	int **board = (int**) calloc (size, sizeof(int*));			//Initializing a dynamic lattice matrix (Rows)

	for (i=0 ; i < size ; i++)
	{
		board[i] = (int*) calloc (size, sizeof(int));			//Initializing a dynamic lattice matrix (Columns)
	}

	for (i=0 ; i < size; i++)						//A for-loop for initializing the percolation sites
	{
		for (j=0 ; j < size ; j++)
		{
			if (ran1(&idum1) < p)					//If the generated random number is lesser than p then assign the cell to 1
				board[i][j] = 1;
			else							//otherwise assign to zero
				board[i][j] = 0;
			board_file  << board[i][j] << "\t";			//Write the resulting generated board to the stream file
			if (j == size-1)
				board_file << "\n";
		}
	}
	board_file.close();							//Closing the streaming text files
	return board;
}
//-----------------End of Board function------------//
