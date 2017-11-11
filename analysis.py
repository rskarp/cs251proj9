# Riley Karp
# analysis.py
# 4/14/2017

import numpy as np
import scipy.stats
import scipy.cluster
import data
import PCAData
import random
import sys
import math

def saveClusters( d, codes, filename ):
	'''Takes in a data object, list of cluster ids, and a filename, and saves the
	data to a file with the cluster ids as the last column.
	'''
	d.addColumn( 'Categories', 'numeric', codes )
	d.write( filename, d.get_raw_headers() )
	if 'Categories' in d.get_raw_headers():
		print True
	else:
		print False

def kmeans_numpy( d, headers, k, whiten = True ):
	'''Takes in a Data object, a set of headers, and the number of clusters to create
	Computes and returns the codebook, codes, and representation error.
	'''
	A = d.get_data( headers )
	W = scipy.cluster.vq.whiten(A)
	codebook , bookerror = scipy.cluster.vq.kmeans( W, k )
	codes , error = scipy.cluster.vq.vq( W , codebook )
	
	return codebook, codes, error
	
def kmeans_init( data, k, labels = None ):
	'''Takes in a numpy matrix of data and the number of clusters to calculate
	the initial cluster means. Returns a matrix of K rows of initial cluster means.
	'''
	#get cluster labels
	if labels == None:
		idx = []
		for i in range( k ):
			id = random.randint(0,k)
			if id not in idx:
				idx.append( id )
				
		#calculate means	
		means = []
		for i in idx:
			m = data[int(i),0:].tolist()[0]
			means.append( m )
		means = np.matrix( means )
	else:
		idx = labels
		means = np.matrix(np.zeros( [ k,data.shape[1] ] ))
		indexes = np.array(labels.T)[0]
		for i in range(k):
			means[i,:] = np.mean( data[indexes==i,:],axis=0 )
	return means #numpy matrix with K rows	
	
def kmeans_classify( data, means ):
	'''Takes in data and cluster means. Returns matrices of closest cluster ids
	and distances to closest cluster for each data point
	'''
	dist = np.matrix(np.zeros( [ data.shape[0],means.shape[0] ] ))

	for m in range( means.shape[0] ): #loop through rows of means
		d = np.sum(np.square(data - means[m,:]),axis=1)
		dist[:,m] = d
		
	ids = np.argmin( dist,axis=1 )
	dist = np.sqrt(np.min( dist, axis=1 ))
		
	return ids, dist #matrix of id values , distances

def kmeans_algorithm(A, means):
	# set up some useful constants
	MIN_CHANGE = 1e-7
	MAX_ITERATIONS = 100
	D = means.shape[1]
	K = means.shape[0]
	N = A.shape[0]

	# iterate no more than MAX_ITERATIONS
	for i in range(MAX_ITERATIONS):
		# calculate the codes
		codes, errors = kmeans_classify( A, means )

		# calculate the new means
		newmeans = np.zeros_like( means )
		counts = np.zeros( (K, 1) )
		indexes = np.array(codes.T)[0]
		for j in range(K):
			newmeans[j,:] = np.mean( A[indexes==j,:],axis=0 )

		# finish calculating the means, taking into account possible zero counts
# 		for j in range(K):
# 			if counts[j,0] > 0.0:
# 				newmeans[j,:] /= counts[j, 0]
# 			else:
# 				newmeans[j,:] = A[random.randint(0,A.shape[0]-1),:]

		# test if the change is small enough
		diff = np.sum(np.square(means - newmeans))
		means = newmeans
		if diff < MIN_CHANGE:
			break

	# call classify with the final means
	codes, errors = kmeans_classify( A, means )

	# return the means, codes, and errors
	return (means, codes, errors)
	
def kmeans(d, headers, K, whiten=True, categories=None ):
	'''Takes in a Data object, a set of headers, and the number of clusters to create
	Computes and returns the codebook, codes and representation errors. 
	If given an Nx1 matrix of categories, it uses the category labels 
	to calculate the initial cluster means.
	'''
	A = d.get_data( headers )
	if whiten:
		W = scipy.cluster.vq.whiten( A )
	else:
		W = A
	codebook = kmeans_init( W, K, categories )
	codebook, codes, errors = kmeans_algorithm( W, codebook )
	
	return codebook, codes, errors

def pca( d, headers, normalized = True ):
	#takes in a data object, list of column headers, and optional normalized boolean.
	#returns a PCAData object with the original headers, projected data, eigen values,
	#eigen vectors, and data means.
	#data
	if normalized:
		A = normalize_columns_separately( headers,d )
	else:
		A = d.get_data(headers)
	#means
	m = A.mean(axis=0)
	#difference matrix
	D = A-m
	#transformation matrix
	U,S,V = np.linalg.svd( D, full_matrices=False )
	#eigen values
	evals = np.matrix( (S*S)/(A.shape[0]-1) )
	#eigen vectors
	evecs = V
	#projected data
	pdata = D*V.T
	#PCAData object
	return PCAData.PCAData( headers, pdata, evals, evecs, m )

def linear_regression( d, ind, dep ):
	#takes a data set, list of independent headers, and dependent header
	#returns fit, sse, r2, t, and p of the multiple linear regression
	y = d.get_data( [dep] )
	A = d.get_data( ind )
	
	ones = []
	for i in range( A.shape[0] ):
		ones.append( 1 )
	ones = np.matrix( ones ).T
	A = np.hstack( [A,ones] )
	
	AAinv = np.linalg.inv( np.dot(A.T,A) )
	
	x = np.linalg.lstsq( A,y )
	
	b = x[0]
	N = y.shape[0] #rows of y
	C = b.shape[0] #rows of b
	df_e = N-C #degrees of freedom of error
	df_r = C-1 #degrees of freedom of model fit
	
	error = y - np.dot( A,b )
	
	sse = np.dot( error.T,error) / df_e #1x1 matrix
	
	stderr = np.sqrt( np.diagonal( sse[0,0]*AAinv ) ) #Cx1 matrix
	
	t = b.T/stderr #t-statistic
	
	p = 2*( 1 - scipy.stats.t.cdf(abs(t),df_e) ) #prob of random relationship
	
	r2 = 1 - error.var() / y.var()
	
	return { 'b':b, 'sse':sse[0][0], 'r2':r2, 't':t[0], 'p':p[0] }
		
def data_range( headers,d ):
	#returns a list of lists containing the min and max values of each column
	ranges = []
	data = d.get_data(headers)
	for i in range( d.get_num_columns() ):
		col = data[0:,i:i+1]
		if col.size > 0:
			ranges.append( [ col.min(),col.max() ] )
	return ranges
	
def mean( headers,d ):
	#returns a list containing the mean value for each column
	means = []
	data = d.get_data(headers)
	for i in range( d.get_num_columns() ):
		if data[0:,i:i+1].size > 0:
			means.append( data[0:,i:i+1].mean() )
	return means
	
def stdev( headers,d ):
	#returns a list containing the standard deviation for each column
	stdev = []
	data = d.get_data(headers)
	for i in range( d.get_num_columns() ):
		if data[0:,i:i+1].size > 0:
			stdev.append( data[0:,i:i+1].std() )
	return stdev
	
def median( headers,d ):
	#returns a list containing the median value for each column
	meds = []
	data = d.get_data(headers)
	for i in range( d.get_num_columns() ):
		if data[0:,i:i+1].size > 0:
			meds.append( np.median( data[0:,i:i+1].A ) )
	return meds
	
def normalize_columns_separately( headers,d ):
	#normalizes each column so the min maps to 0 and the max maps to 1
	data = d.get_data(headers)
	norm = np.matrix([], dtype = float)
	norm.shape = ( d.get_raw_num_rows(), 0 ) #reshape so we can add cols using hstack
	for i in range( d.get_num_columns() ):
		col = data[0:,i:i+1]
		if col.size > 0:
			col = col - col.min()
			if col.max() != 0:
				col = col/col.max()
			norm = np.hstack( [norm, col] )
	return norm
	
def normalize_columns_together( headers,d ):
	#normalizes all the data so the min maps to 0 and the max maps to 1
	data = d.get_data(headers)
	if data.size > 0:
		norm = data - data.min()
		if data.max() != 0:
			norm = norm/data.max()
		return norm
		
def testLinReg():
	#prints linReg data in terminal for the 3 test CSV files
	for file in [ 'data-clean.csv','data-good.csv','data-noisy.csv' ]:
		d = data.Data( file )
		print '-----------------------------------------------------'
		print '\t' , file
		print '-----------------------------------------------------'
		linReg = linear_regression( d, ['X0','X1'], 'Y' )
		print 'm0: ' , float(linReg['b'][0])
		print 'm1: ' , float(linReg['b'][1])
		print 'b: ' , float(linReg['b'][2])
		print 'sse: ' , float(linReg['sse'])
		print 'r2: ' , linReg['r2']
		print 't ' , linReg['t'].tolist()[0]
		print 'p: ' , linReg['p']
		
def myLinReg():
	#prints linReg data in terminal for nfldata.csv
	d = data.Data( 'nfldata.csv' )
	print '-----------------------------------------------------'
	print '\tnfldata.csv'
	print '-----------------------------------------------------'
	ind = ['Make Playoffs','Win Division','1st Round Bye']
	linReg = linear_regression( d, ind, 'Win Super Bowl' )
	print 'm0: ' , float(linReg['b'][0])
	print 'm1: ' , float(linReg['b'][1])
	print 'm2: ' , float(linReg['b'][2])
	print 'b: ' , float(linReg['b'][3])
	print 'sse: ' , float(linReg['sse'])
	print 'r2: ' , linReg['r2']
	print 't ' , linReg['t'].tolist()[0]
	print 'p: ' , linReg['p']
	
def acLinReg():
	#prints linReg data in terminal for AustraliaCoast.csv
	d = data.Data( 'AustraliaCoast.csv' )
	print '-----------------------------------------------------'
	print '\tAustraliaCoast.csv'
	print '-----------------------------------------------------'
	ind = ['minairtemp','maxairtemp','minsst','maxsst']
	linReg = linear_regression( d, ind, 'Latitude' )
	print 'm0: ' , float(linReg['b'][0])
	print 'm1: ' , float(linReg['b'][1])
	print 'm2: ' , float(linReg['b'][2])
	print 'b: ' , float(linReg['b'][3])
	print 'sse: ' , float(linReg['sse'])
	print 'r2: ' , linReg['r2']
	print 't ' , linReg['t'].tolist()[0]
	print 'p: ' , linReg['p']
	
# if __name__ == '__main__':
#	testLinReg()
#	myLinReg()
	acLinReg()
