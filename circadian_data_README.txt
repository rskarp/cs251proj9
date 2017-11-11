README for circadian_data.csv

The data is taken from a slice of a mouse brain and was first reported in 

Webb, Angelo, Huettner, Herzog, PNAS, 2009.

The experiment records the bioluminescence from each of 123 cells in 3 experimental conditions:
1) the base condition (144 data pts sampled 1 hour apart)
2) after treating the slice with a toxin (144 data pts sampled 1 hour apart)
3) after washing out the toxin (142 data pts sampled 1 hour apart)

The data is discussed in more detail in

Webb, Taylor, Thoroughman, Doyle III, Herzog, PLoS Comput Biol, 2012.

The data file has one row for each of 123 cells. The features are

X: the x-position of the cell in the dish (units are pixels, sort of)
Y: the y-position of the cell in the dish (units are pixels, sort of)
L2R1: Indicates whether the cell is in the left half of the slice (value is 2) or the right half (value is 1)
B1 ... B144: the bioluminescence at that hour in the base condition
T1 ... T144: the bioluminescence at that hour in the toxin-treated condition
W1 ... W142: the bioluminescence at that hour in the washout condition