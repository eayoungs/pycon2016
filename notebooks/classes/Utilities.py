# Utilities module for pycon2016 tutorial
from geopy.distance import vincenty
import numpy as np
import pandas as pd

# return a distance matrix dataframe for all points in group dataframe
# expect group to have columns latitude and longitude
def distance_matrix(group, latcol,longcol):
	group_matrix = pd.DataFrame(index = group.index, columns = group.index)  
	for c in group_matrix.columns:
		lat1 = group.columns.get_loc(latcol)
		long1 = group.columns.get_loc(longcol)
		lat2 = group[latcol][c]
		long2 = group[longcol][c]
		group_matrix[c] = group.apply(lambda x: vincenty((x[lat1], x[long1]), (lat2,long2)).miles, axis=1)
	return group_matrix

# return a deduplicated dataframe based on distance between observations
# when matches are found, drop the observation with the least recent lastupdateddate
# assumes group has columns latitude, longitude, and lastupdateddate
def dedupe_by_distance(group, limit, latcol, longcol, lastupdatecol):
	distances = distance_matrix(group, latcol, longcol)
	df_out = group

	# examine upper triangle for distance measurements under the specified limit
	matches = np.where((np.triu(distances) < limit) & (np.triu(distances) > 0))
	for pair in zip(matches[0],matches[1]):
		pair_sub = df_out.loc[np.array(pair)]

		# if a member of the matched pair has already been dropped pair_sub will
		# contain an NaN row, drop
		pair_sub = pair_sub.dropna()

		# if only one pair member remains, do not remove. skip to the next pair
		if pair_sub[lastupdatecol].count() < 2:
			continue 

		least_recent = pair_sub[pair_sub[lastupdatecol] != max(pair_sub[lastupdatecol])]
		if least_recent.empty :
			# both observations have the same updated date, drop first one
			df_out = df_out.drop(pair_sub.index[0])
		else :
			df_out = df_out.drop(least_recent.index)

	return df_out