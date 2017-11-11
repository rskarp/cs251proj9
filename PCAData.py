# Riley Karp
# data.py
# 2/20/2017

import sys
import csv
import numpy as np
import data

#class that can read a csv data file and provide information about it
class PCAData( data.Data ):

	def __init__(self, origHeaders, projData, evals, evecs, origMeans ):
		#creates a PCAData object by initializing the fields of the Data object
		data.Data.__init__(self)
		
		#create and initialize fields
		self.evecs = evecs
		self.evals = evals
		self.means = origMeans
		self.headers = origHeaders
		self.matrix_data = projData
		
		#old fields
		self.raw_headers = [] # e0,e1,etc...
		self.raw_types = [] # all numeric
		self.raw_data = projData.tolist()
		self.header2raw = {} # raw_headers
		self.header2matrix = {} # origHeaders
		
		for i in range( len(self.headers) ):
			self.raw_headers.append( 'e' + str(i) )
			self.header2raw[ 'e' + str(i) ] = i
			self.raw_types.append( 'numeric' )
			self.header2matrix[ self.headers[i] ] = i
			self.matrix2header[ i ] = self.headers[i]
			
	def write( self, filename ):
		#writes all the PCA information to the specified file
		file = filename + '.csv'
		f = open( file, 'wb' )
		writer = csv.writer( f, delimiter=',', quoting=csv.QUOTE_MINIMAL )
		
		heads = ['E-vec','E-val','Cumulative']
		for h in self.get_headers():
			heads.append( h )
		
		types = ['enum','string','percent']
		for i in range( len(self.get_raw_headers()) ):
			types.append( 'numeric' )
			
		writer.writerow(heads)
		writer.writerow(types)
				
		total = 0
		sum = 0
		for i in range( self.get_eigenvalues().size ):
			total += self.get_eigenvalues()[0,i]
			
		for i in range( self.get_eigenvectors().shape[1] ):
			sum += self.get_eigenvalues()[0,i]
			cum = round( (sum/total) , 4 )
			row = [ 'e'+str(i), round( self.get_eigenvalues()[0,i] , 4 ), cum ]
			for j in range( self.get_eigenvectors().shape[0] ):
				row.append( round( self.get_eigenvectors()[i,j],4) )
			writer.writerow(row)
		
		f.close()

# 	def write( self, filename ):
# 		#second write method. writes all the PCA information to the specified file
# 		file = filename + '.csv'
# 		f = open( file, 'wb' )
# 		writer = csv.writer( f, delimiter=',', quoting=csv.QUOTE_MINIMAL )
# 		
# 		types = []
# 		heads = []
# 		for i in range( self.matrix_data.shape[1] ):
# 			heads.append( 'e'+str(i) )
# 			types.append( 'numeric' )
# 			
# 		writer.writerow(heads)
# 		writer.writerow(types)
# 
# 		print self.get_eigenvectors().shape
# 		print self.matrix_data.shape
# 		for i in range( self.matrix_data.shape[1] ):
# 			row = self.matrix_data[i,:].tolist()[0]
# 			writer.writerow(row)
# 		
# 		f.close()
		
	def get_eigenvalues(self):
		#returns a copy of the eigenvalues as a single-row numpy matrix
		return self.evals
		
	def get_eigenvectors(self):
		#returns a copy of the eigenvectors as a numpy matrix with the eigenvectors as rows
		return self.evecs
		
	def get_data_means(self):
		#returns the means for each column in the original data as a single row numpy matrix
		return self.means
		
	def get_data_headers(self):
		#returns a copy of the list of the headers from the original data used to generate the projected data
		return self.headers