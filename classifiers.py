# Template by Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Classifier class and child definitions

# Riley Karp
# classifiers.py
# 5/12/17

import sys
import data
import analysis as an
import numpy as np
import scipy.cluster

class Classifier:

	def __init__(self, type):
		'''The parent Classifier class stores only a single field: the type of
		the classifier.	 A string makes the most sense.

		'''
		self._type = type

	def type(self, newtype = None):
		'''Set or get the type with this function'''
		if newtype != None:
			self._type = newtype
		return self._type

	def confusion_matrix( self, truecats, classcats ):
		'''Takes in two Nx1 matrices of zero-index numeric categories and
		computes the confusion matrix. The rows represent true
		categories, and the columns represent the classifier output.
		'''
		trueunique, truemap = np.unique( np.array( truecats ), return_inverse= True )
		numCats = len( trueunique )
		cmat = np.matrix( np.zeros( [ numCats,numCats ] ) )		
		for i in range( classcats.shape[0] ):
			cmat[ truemap[i], classcats[i,0] ] += 1
		cmat = np.concatenate( (np.matrix( trueunique ).T,cmat),axis=1 )
				
		return cmat

	def confusion_matrix_str( self, cmtx ):
		'''Takes in a confusion matrix and returns a string suitable for printing.'''
		labels = cmtx[:,0]
		s = '\nConfusion Matrix:\n'
		for i in range( cmtx.shape[1] ):
			for j in range( cmtx.shape[1] ):
				if i == 0:
					if j == 0:
						s += 'Actual->'
					else:
						s += '\t' + str( int( labels[j-1,0] ) )
				else:
					s += '\t' + str( int( cmtx[i-1,j] ) )
			s += '\n'
    
		return s

	def __str__(self):
		'''Converts a classifier object to a string.  Prints out the type.'''
		return str(self._type)



class NaiveBayes(Classifier):
	'''NaiveBayes implements a simple NaiveBayes classifier using a
	Gaussian distribution as the pdf.

	'''

	def __init__(self, dataObj=None, headers=[], categories=None):
		'''Takes in a Data object with N points, a set of F headers, and a
		matrix of categories, one category label for each data point.'''

		# call the parent init with the type
		Classifier.__init__(self, 'Naive Bayes Classifier')
		
		self.headers = headers #headers used for classification
		self.C = None #number of classes
		self.F = None #number of features
		self.class_labels = None #original class labels
		
		# unique data for the Naive Bayes: means, variances, scales
		self.class_means = None
		self.class_vars = None
		self.class_scales = None
		
		if dataObj != None:
			A = dataObj.getData(headers)
			self.build( A,categories )

	def build( self, A, categories ):
		'''Builds the classifier give the data points in A and the categories'''
		
		# figure out how many categories there are and get the mapping (np.unique)
		unique, mapping = np.unique( np.array( categories.T ), return_inverse= True )
		self.C = len( unique )
		self.F = A.shape[1]
		self.class_labels = unique
		# create the matrices for the means, vars, and scales
		# the output matrices will be categories (C) x features (F)
		self.class_means = np.matrix( np.empty([self.C,self.F]) )
		self.class_vars = np.matrix( np.empty([self.C,self.F]) )
		self.class_scales = np.matrix( np.empty([self.C,self.F]) )
		
		# compute the means/vars/scales for each class
		for i in range( self.C ):
			for j in range( self.F ):
				self.class_means[i,:] = np.mean( A[mapping==i,:],axis=0 )
				vars = np.var( A[mapping==i,:],axis=0 )
				self.class_vars[i,:] = vars
				if vars.all() != 0:
					self.class_scales[i,:] = 1/np.sqrt( 2*np.pi*vars )
				else:
					self.class_scales[i,:] = 0
	
		return

	def classify( self, A, return_likelihoods=False ):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_likelihoods
		is True, it also returns the NxC likelihood matrix.

		'''
		# error check to see if A has the same number of columns as
		# the class means
		if A.shape[1] != self.class_means.shape[1]:
			print 'Error: different number of data columns and means.'
			return
		
		# make a matrix that is N x C to store the probability of each
		# class for each data point
		P = np.matrix( np.empty([A.shape[0],self.C]) ) 

		# calculate the probabilities by looping over the classes
		for i in range( self.C ):
			P[:,i] = np.prod( np.multiply(self.class_scales[i,:], 
				np.exp( np.multiply(-1.0,
				np.divide( np.square(A - self.class_means[i,:]),
				np.multiply(2, self.class_vars[i,:]) )) )), axis = 1 )

		# calculate the most likely class for each data point
		cats = np.argmax( P, axis=1 ) # take the argmax of P along axis 1

		# use the class ID as a lookup to generate the original labels
		labels = self.class_labels[cats]

		if return_likelihoods:
			return cats, labels, P

		return cats, labels

	def __str__(self):
		'''Make a pretty string that prints out the classifier information.'''
		s = "\nNaive Bayes Classifier\n"
		for i in range(self.C):
			s += 'Class %d --------------------\n' % (i)
			s += 'Mean	: ' + str(self.class_means[i,:]) + "\n"
			s += 'Var	: ' + str(self.class_vars[i,:]) + "\n"
			s += 'Scales: ' + str(self.class_scales[i,:]) + "\n"

		s += "\n"
		return s
		
	def write(self, filename):
		'''Writes the Bayes classifier to a file.'''
		# extension
		return

	def read(self, filename):
		'''Reads in the Bayes classifier from the file'''
		# extension
		return

	
class KNN(Classifier):

	def __init__(self, dataObj=None, headers=[], categories=None, K=None):
		'''Take in a Data object with N points, a set of F headers, and a
		matrix of categories, with one category label for each data point.'''

		# call the parent init with the type
		Classifier.__init__(self, 'KNN Classifier')
		
		# store the headers used for classification
		self.headers = headers
		# number of classes and number of features
		self.C = None
		self.F = None
		# original class labels
		self.class_labels = None
		# unique data for the KNN classifier: list of exemplars (matrices)
		self.exemplars = []
		
		if dataObj != None:
			self.build( dataObj.get_data( headers ), categories, K )

	def build( self, A, categories, K = None ):
		'''Builds the classifier give the data points in A and the categories'''

		# figure out how many categories there are and get the mapping (np.unique)
		unique, mapping = np.unique( np.array( categories.T ), return_inverse= True )
		self.C = len( unique )
		self.F = A.shape[1]
		self.class_labels = unique
		for i in range( self.C ):
			if K == None:
				self.exemplars.append( A[mapping==i,:] )
			else:
# 				codebook = an.kmeans_init( A[mapping==i,:],K )
				codebook, distortion = scipy.cluster.vq.kmeans( A[mapping==i,:],K )
				self.exemplars.append( codebook )

		return

	def classify(self, A, K=3, return_distances=False):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_distances is
		True, it also returns the NxC distance matrix.

		The parameter K specifies how many neighbors to use in the
		distance computation. The default is three.'''

		# error check to see if A has the same number of columns as the class means
		if A.shape[1] != self.exemplars[0].shape[1]:
			print 'Error: different number of data columns and means.'
			return

		# make a matrix that is N x C to store the distance to each class for each data point
		N = A.shape[0]
		D = np.matrix( np.empty( [N,self.C] ) )
		
		for i in range( self.C ):
			# make a temporary matrix that is N x M where M is the number of examplars (rows in exemplars[i])
			temp = np.matrix( np.empty( [ N,self.exemplars[i].shape[0] ] ) )
			# calculate the distance from each point in A to each point in exemplar matrix i (for loop)
			for j in range( self.exemplars[i].shape[0] ):
				temp[:,j] = np.sqrt( np.sum(np.square(A - self.exemplars[i][j,:]),axis=1 ) )
			# sort the distances by row
			temp = np.sort( temp, axis=1 )
			# sum the first K columns
			D[:,i] = np.sum( temp[:,:K],axis=1 )
			# this is the distance to the first class

		# calculate the most likely class for each data point
		cats = np.argmin( D,axis=1 ) # take the argmin of D along axis 1

		# use the class ID as a lookup to generate the original labels
		labels = self.class_labels[cats]

		if return_distances:
			return cats, labels, D

		return cats, labels

	def __str__(self):
		'''Make a pretty string that prints out the classifier information.'''
		s = "\nKNN Classifier\n"
		for i in range(self.C):
			s += 'Class %d --------------------\n' % (i)
			s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
			s += 'Mean of Exemplars	 :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

		s += "\n"
		return s


	def write(self, filename):
		'''Writes the KNN classifier to a file.'''
		# extension
		return

	def read(self, filename):
		'''Reads in the KNN classifier from the file'''
		# extension
		return
	

