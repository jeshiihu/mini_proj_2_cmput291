import sqlite3

def getFDTableName(conn, c):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'input_fds_%';")
	result = c.fetchone()

	if not result:
		print "Error: could not get Functional Dependancy Table Name"
		exit()

	return result[0]

def getFDDictionary(conn, c, tableName):
	query = 'SELECT * FROM ' + tableName + ';'
	c.execute(query)
	results = c.fetchall()

	if not results:
		print "Error: unable to get data from table " + tableName
		exit()

	fdDict = {'LHS' : 'RHS'} #dummy to start the table
	for r in results:
		fdDict[r['LHS']] = r['RHS']

	# for key in fdDict: # keys = LHS
	# 	print key + " --> " + fdDict[key]

	return fdDict

def computeMinimalCover(conn, c):
	print "Computing minimal cover"

	# select the FDs table
	fdTableName = getFDTableName(conn, c)
	fdDict = getFDDictionary(conn, c, fdTableName)
	
	for key in fdDict: # keys = LHS
		print key + " --> " + fdDict[key]

	# 1. make the RHS of each FD into a single attribute
	# 2. Elimate redundant attribute from LHS
	# 3. Delete redundant FDs