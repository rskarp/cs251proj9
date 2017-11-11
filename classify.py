# Riley Karp
# classify.py
# 5/12/17

import sys
import data
import classifiers

def main(argv):
	#usage
	if len(argv) < 4:
		print 'Usage: python %s <training data file> <test data file> <nb or knn> <optional training category file> <optional test category file>' % (argv[0])
		exit(-1)
	
	#store classifier type
	classifier = argv[3]
	
	if classifier != 'nb' and classifier != 'knn':
		print 'Usage:  python %s <training data file> <test data file> <nb or knn> <optional training category file> <optional test category file>' % (argv[0])
		exit(-1)
		
	print '\nReading data files'
	
	#read the training and test sets
	dtrain = data.Data(argv[1])
	dtest = data.Data(argv[2])

	#get the categories and the training data train and the test data test
	if len(argv) > 5:
		traincatdata = data.Data(argv[4])
		testcatdata = data.Data(argv[5])
		
		traincats = traincatdata.get_data( [traincatdata.get_headers()[0]] )
		testcats = testcatdata.get_data( [testcatdata.get_headers()[0]] )
		
		train = dtrain.get_data( dtrain.get_headers() )
		test = dtest.get_data( dtest.get_headers() )
		
		headers = dtest.get_headers()
	else:
		#assume the categories are the last column
		traincats = dtrain.get_data( [dtrain.get_headers()[-1]] )
		testcats = dtest.get_data( [dtest.get_headers()[-1]] )
		
		train = dtrain.get_data( dtrain.get_headers()[:-1] )
		test = dtest.get_data( dtest.get_headers()[:-1] )
		
		headers = dtest.get_headers()[:-1]
	
	#create classifier using training set
	if classifier == 'knn':
		
		#get k
		k = raw_input('How many nearest neighbors? (default=3) Type number then press enter: ')
		if k == '':
			k = 3
		else:
			k = abs( int(k) )
		
		#make new KNN classifier
		knntrain = classifiers.KNN()

		print '\nTraining the classifier'
		# build the classifier from training set
		knntrain.build( train, traincats, k )

		print '\nClassifying training data'
		# classify training set print confusion matrix
		trainCat, trainLab = knntrain.classify( train )
		
		print '\nBuilding training confusion matrix'
		traincmat = knntrain.confusion_matrix( traincats, trainCat )
		print knntrain.confusion_matrix_str( traincmat )
		
		print '\nClassifying testing data'
		# classify test set and print confusion matrix
		testCat, testLab = knntrain.classify( test )
		
		print '\nBuilding testing confusion matrix'
		testcmat = knntrain.confusion_matrix( testcats, testCat )
		print knntrain.confusion_matrix_str( testcmat )
		
		#write test data set and categories to CSV file
		filename = raw_input('Type filename for test data, then press enter: ')

		print '\nSaving test data'
		dtest.addColumn( 'Categories', 'numeric', testCat.T.tolist()[0] )
		
		headers.append( 'Categories' )
		
		dtest.write( filename, headers )
		
	else: # classifier is nb
		
		#make new naive bayes classifier
		nbtrain = classifiers.NaiveBayes()
		
		print '\nTraining the classifier'
		# build the classifier from training set
		nbtrain.build( train, traincats )

		print '\nClassifying training data'
		# classify training set print confusion matrix
		trainCat, trainLab = nbtrain.classify( train )
		
		print '\nBuilding training confusion matrix'
		traincmat = nbtrain.confusion_matrix( traincats, trainCat )
		print nbtrain.confusion_matrix_str( traincmat )
		
		print '\nClassifying testing data'
		# classify test set and print confusion matrix
		testCat, testLab = nbtrain.classify( test )
		
		print '\nBuilding testing confusion matrix'
		testcmat = nbtrain.confusion_matrix( testcats, testCat )
		print nbtrain.confusion_matrix_str( testcmat )
		
		#write test data set and categories to CSV file
		filename = raw_input('Type filename for test data, then press enter: ')

		print '\nSaving test data'
		dtest.addColumn( 'Categories', 'numeric', testCat.T.tolist()[0] )
		
		headers.append( 'Categories' )
		
		dtest.write( filename, headers )
		
if __name__ == "__main__":
    main(sys.argv)