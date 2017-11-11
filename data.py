# Riley Karp
# data.py
# 2/20/2017

import sys
import csv
import numpy as np

#class that can read a csv data file and provide information about it
class Data:

	def __init__(self, filename = None):
		#creates a Data object by initializing the fields and reading the given csv file
		
		#create and initialize fields
		self.raw_headers = []
		self.raw_types = []
		self.raw_data = []
		self.header2raw = {}
		self.matrix_data = np.matrix([])
		self.header2matrix = {}
		self.matrix2header = {} #allows headers to be listed in order in self.get_headers()
		
		if filename != None:
			self.read(filename)
		
	def read(self, filename):
		#reads the given csv file and adds headers, types, and data to their respective fields
		file = open( filename, 'rU' )
		rows = csv.reader( file ) 
		
		#append data to raw_data list field
		for row in rows:
			self.raw_data.append(row)
		file.close()
		
		#strip data to get rid of random spaces
		for row in self.raw_data:
			for j in range( len(row) ):
				row[j] = row[j].strip()
		
		#add headers and types to their respective fields
		self.raw_headers = self.raw_data.pop(0)
		self.raw_types = self.raw_data.pop(0)
		
		#add values to header2raw dictionary & strip header strings
		for item in self.raw_headers:
			self.header2raw[ item ] = self.raw_headers.index(item)
			
		#add numeric values to matrix_data and header2matrix dictionary
		idx = 0
		data = []
		for i in range( len(self.raw_types) ):
			if self.raw_types[i] == 'numeric':
				#add headers and indexes to dictionary
				header = self.raw_headers[i]
				self.header2matrix[header] = idx
				self.matrix2header[idx] = header
				#add data to matrix_data
				data.append([]) #makes new empty row
				for r in range( self.get_raw_num_rows() ):
					data[idx].append( self.raw_data[r][i] )
				idx += 1
		#put data into numpy matrix
		self.matrix_data = np.matrix( data , dtype = float).T
		
	def write( self, filename, headers = [] ):
		#writes the data of the specified headers to a file of the given name
		if len(headers) > 0:
			d = self.get_data( headers )
			file = filename + '.csv'
			f = open( file, 'wb' )
			writer = csv.writer( f, delimiter=',', quoting=csv.QUOTE_MINIMAL )
			
			writer.writerow(headers)
			
			types = []
			for h in headers:
				types.append( self.get_raw_types()[ self.header2raw[h] ] )
			
			writer.writerow(types)
			
			for i in range( d.shape[0] ):
				row = []
				for j in range( len(headers) ):
					if headers[j] in self.header2raw.keys():
						row.append( self.get_raw_value( i, headers[j] ) )
					elif headers[j] in self.header2matrix.keys():
						row.append( round( d[i,j],3 ) )
				if row != []:
					writer.writerow( row )
				
			f.close()
		
	def get_headers(self):
		#returns a list of the headers of columns with numeric data
		headers = []
		for i in range( len(self.matrix2header) ):
			headers.append( self.matrix2header[i] )
		return headers
		
	def get_num_columns(self):
		#returns the number of columns with numeric data
		return len(self.header2matrix)
	
	def get_row(self, rIdx):
		#returns the specified row of numeric data
		if rIdx >= 0 and rIdx < self.get_raw_num_rows():
			return self.matrix_data.tolist()[rIdx]
	
	def get_value(self, rIdx, cString):
		#returns the value of numeric data at the given row,col location
		if rIdx >= 0 and rIdx < self.get_raw_num_rows() and cString in self.header2matrix:
			return self.matrix_data[ rIdx, self.header2matrix[cString] ]
		
	def get_data(self, headers):
		#returns a matrix of numeric data from the columns with the specified list of headers
		d = np.matrix([]) #empty matrix
		d.shape = ( self.get_raw_num_rows(), 0 ) #reshape matrix so we can use hstack
		for h in headers:
			if h in self.header2matrix.keys():
				cIdx = self.header2matrix[h]
				col = self.matrix_data[ 0:, cIdx:cIdx+1 ]
				d = np.hstack( [d,col] )
		return d
		
	def addColumn(self, header, type, points):
		#adds a column of data with the given header, type, and list of data points
		if len(points) == self.get_raw_num_rows():
			self.header2raw[header] = self.get_raw_num_columns()
			self.raw_headers.append(header)
			self.raw_types.append(type)
			for i in range( len(points) ):
				self.raw_data[i].append(points[i])
			if type == 'numeric':
				self.header2matrix[header] = self.get_num_columns()
				col = np.matrix( points ).T
				self.matrix_data = np.hstack( [self.matrix_data, col] )
			
	def get_raw_headers(self):
		#returns a reference to the list of all the headers
		return self.raw_headers
		
	def get_raw_types(self):
		#returns a reference to the list of data types in each column
		return self.raw_types
		
	def get_raw_num_columns(self):
		#returns the total number of columns of data
		return len(self.raw_headers)
		
	def get_raw_num_rows(self):
		#returns the total number of rows of data
		return len(self.raw_data)
		
	def get_raw_row(self, idx):
		#returns the specified row of raw data
		if idx >=0 and idx < self.get_raw_num_rows():
			return self.raw_data[idx]
		
	def get_raw_value(self, rIdx, cString):
		#returns the value at the specified row,col location
		if rIdx >=0 and rIdx < self.get_raw_num_rows():
			return self.raw_data[ rIdx ][ self.header2raw[cString] ]
		
	def toString(self):
		#prints the contents of the Data object by rows and columns
		string = ''
		for item in [self.get_raw_headers(), self.get_raw_types()]:
			for idx in range( self.get_raw_num_columns() ):
				string += item[idx] + '\t'
			string += '\n'
		for row in self.raw_data:
			for idx in range( len(row) ):
				string += row[idx] + '\t'
			string += '\n'
			
		print string
			
def main(filename):
	#tests all the methods of the Data class
	d = Data( filename )
	print '\t Testing Raw Methods'
	print 'd.get_raw_headers: ' , d.get_raw_headers()
	print 'd.get_raw_types: ' , d.get_raw_types()
	print 'd.get_raw_num_columns: ' , d.get_raw_num_columns()
	print 'd.get_raw_row(0): ' , d.get_raw_row(0)
# 	print 'raw_data: ' , d.raw_data
# 	print 'header2raw:' , d.header2raw
# 	d.toString()
	
	headers = ['hi', 'headers', 'in', 'spaces', 'bye']
	
	print '\n \t Testing Numeric Methods'
	print 'd.get_headers: ' , d.get_headers()
	print 'd.get_num_columns: ' , d.get_num_columns()
	print 'd.get_row(0): ' , d.get_row(0)
	print 'd.get_value( 1, "bad" ): ' , d.get_value( 1, 'bad' )
	print 'd.get_data( headers ): \n' , d.get_data( headers )
		
	print '\n \t Testing Analysis Methods'
	print 'range: ' , a.data_range(headers,d)
	print 'median: ' , a.median(headers,d)
	print 'mean: ' , a.mean(headers,d)
	print 'stdev: ' , a.stdev(headers,d)
	print 'normalize_columns_separately: \n' , a.normalize_columns_separately(headers,d)
	print 'normalize_columns_together: \n' , a.normalize_columns_together(headers,d)
	
	print '\n \t Testing addColumn'
	print 'd.get_raw_headers: ' , d.get_raw_headers()
	print 'd.get_raw_types: ' , d.get_raw_types()
	print 'd.raw_data: ' , d.raw_data
	print 'd.get_data( headers ): \n' , d.get_data( headers )
	print '\t adding column'
	d.addColumn( 'newCol', 'numeric', [3,1,4] )
	headers.append( 'newCol' )
	print 'd.get_raw_headers: ' , d.get_raw_headers()
	print 'd.get_raw_types: ' , d.get_raw_types()
	print 'd.raw_data: ' , d.raw_data
	print 'd.get_data( headers ): \n' , d.get_data( headers )
	
def testWrite(filename):
	d = Data(filename)
	headers = d.get_raw_headers()[0:5]
	d.write( 'testWrite',headers )
		 
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: python %s <csv_filename>" % sys.argv[0]
		print "		  where <csv_filename> specifies a csv file"
		exit()
# 	main( sys.argv[1] )
	testWrite( sys.argv[1] )