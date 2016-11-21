import sqlite3

def getFDTableName(conn, c):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'input_fds_%';")
	result = c.fetchone()

	if not result:
		print "Error: could not get Functional Dependancy Table Name"
		exit()

	return result[0]

def getFDSet(conn, c, tableName):
	query = 'SELECT * FROM ' + tableName + ';'
	c.execute(query)
	results = c.fetchall()

	if not results:
		print "Error: unable to get data from table " + tableName
		exit()

	fdSet = set()
	for r in results:
		fdSet.add((r['LHS'], r['RHS']))

	# # ----------------------- TESTING -----------------------
	# for fd in fdSet: # keys = LHS
	# 	print fd

	return fdSet

def getClosure(lhs, fdSet):
	return ''

def computeMinimalCover(conn, c):
	print "Computing minimal cover"

	# select the FDs table
	fdTableName = getFDTableName(conn, c)
	fdSet = getFDSet(conn, c, fdTableName)

	# 1. make the RHS of each FD into a single attribute
	tempSet = set()
	for fd in fdSet:
		if "," in fd[1]:
			rhsList = fd[1].split(',')
			for c in rhsList:
				tempSet.add((fd[0],c))
		else:
			tempSet.add(fd)
	fdSet = tempSet

	# 2. Elimate redundant attribute from LHS
	tempSet = set()
	for fd in fdSet:
		if ',' in fd[0]: # possible redundancy
			lhsList = fd[0].split(',')
			for c in lhsList:
				#eliminate from lhs
				tempLHS = lhsList.remove(c)
				lhs = ''.join(tempLHS)

				rhsClosure = getClosure(lhs, fdSet)
				# check if we can get a closure that gets us the rhs

		else:
			tempSet.add(fd)
	fdSet = tempSet

	# 3. Delete redundant FDs



