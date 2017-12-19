/*
   Hoshen_Kopelman.cpp
   Purpose: Identifiy clusters on a square lattice

   @author Yousof Mardoukhi
   @version 1.1 12/12/2017
*/

/*
   Returns a vector containing the clusters' labels
   @params -board The initialised underlying square lattice
           -size The size of the underlying lattice
	   -label_board An empty square lattice to store temporarily the label of each site

   @return -labels A vector containing the labels of the clusters
           
*/
//------------BEGIN OF HOSHEN-KOPELMAN FUNC---------//
vector<int> hoshen_kopelman(int **board, int size, int **label_board)		//Defining a function which does the Hoshen-Kopelman algorithm
{
	vector<int> labels;							//Initialising an integer vector
	int pos;								//pos is an integer variable which stores the index of a specific label
	int new_label = 1;							//new_label stores the label of the most recent found cluster
	
	for (int i=0; i<size; i++)						//A for-loop going through each individual cell of the lattice (board variable which stores the geometry of the percolation space)
	{
		for (int j=0; j<size; j++)
		{
			if (board[i][j] == 1)					//If the site ij is occupied the following conditions may happen
			{
				
				int left = (i==0 ? 0 : board[i-1][j]);		//First check if the cell is located at the boundary (row)
				int above = (j==0 ? 0 : board[i][j-1]);		//First check if the cell is located at the boundary (column)
				
				switch (above + left)				//Switch to the appropriate case
				{
					case 0:					//Case zero, in which the neighbouring cell (up and left) are unoccupied
						labels.push_back(new_label);	//The cell is assigned a new label (the value of the new_label) and the label is stored in the vector 'labels'
						pos = find(labels.begin(), labels.end(),new_label) - labels.begin();
										//The index of the new_label is found and is stored in the variable pos
						label_board[i][j] = labels[pos];//The value of the new_label is assigned ot the cell ij on the label board
						new_label++;			//The value of the new_label is increased by one
						break ;											//Exit the switch environment
					
					case 1:					//Case one, in which one of the neighbouring cell (up or left) is occupied
						if (left == 1)			//If the left cell is occupied 
							label_board[i][j] = label_board[i-1][j];
										//The label of the left cell is assigned to the ij cell
						else 				//If the above cell is occupied
							label_board[i][j] = label_board[i][j-1];
										//The label of the above cell is assigned to the ij cell
						break ;				//Exit the switch environment
					
					case 2:					//Case two, in which both neighbouring cells (up and left) are occupied
						int max_label = max(label_board[i-1][j], label_board[i][j-1]);
										//Stores the maximum label number of the two neighbouring cells
						int min_label = min(label_board[i-1][j], label_board[i][j-1]);
										//Stores the minimum label number of the two neighbouring cells
						if (max_label == min_label)	//If the the two neighbouring cells have the same value
						{
							label_board[i][j] = max_label;
										//Assign the label which the two neighbouring cells
							pos = find(labels.begin(), labels.end(), min_label) - labels.begin();
										//The index of the min_value is extracted and stored in variable pos
						}
						else 				//If the labels of the two neighbouring cells are different all the previously connected cells changes their label number accordingly
						{
							#pragma omp parallel for //OpenMP parallel loop
							for (int k=0; k<=i; k++)//A for loop going through all the previous cells before the ij cell to change the label class
							{
								for (int l=0; l<size; l++)
								{
									if (label_board[k][l] == min_label)
										//If the previously labelled cell has the man_value as the label number
									{
										label_board[k][l] = max_label;
										//Its label number changes to the max_label value
									}
								}
							}
							label_board[i][j] = max_label;
										//At last, change the label of the cell ij to max_label
							pos = find(labels.begin(), labels.end(), min_label) - labels.begin();
										//The index of the min_label is extracted and stored in variable pos
							labels.erase(labels.begin()+ pos);
										//Remove the min_label from the labels array
						}
						break;
				}
			}
		}
	}
	return labels;
}
//------------END OF HOSHEN-KOPELMAN FUNC---------//
