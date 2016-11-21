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
	# working with sets, so no need to worry about duplicates
	closure = set(lhs) # eg. BH+ = BH
	# print ''.join(lhs) + "+ = " + ''.join(closure)

	for fd in fdSet: 
		tempLHS = fd[0].split(',')
		foundLHS = True

		for c in tempLHS:	# find if we can add the RHS to the closure
			if c not in closure:
				foundLHS = False
				break

		if foundLHS: # we can add it!
			closure.add(fd[1])

	if(lhs == closure): # we have iterated through the whole thing and cant add anymore!
		return closure
	else:
		return getClosure(closure, fdSet)

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
			for c in fd[0].split(','):
				#eliminate from lhs
				templhs = fd[0].split(',')
				# print "Before Removal: " + ''.join(templhs)
				# print "... removing " + c
				templhs.remove(c)
				# print "After Removal: " + ''.join(templhs)

				closure = getClosure(templhs, fdSet)
				# print "Original: " + fd[0] + "-->" + fd[1]
				# print ''.join(templhs) + "+ = " + ''.join(closure)

				if fd[1] in closure: # then we know that single attribute is redundant
					print c + " is redundant in " + fd[0] + " --> " + fd[1]
				# check if we can get a closure that gets us the rhs
		else:
			tempSet.add(fd)
	fdSet = tempSet

	# 3. Delete redundant FDs



