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

# =================================== 1. make the RHS of each FD into a single attribute ===================================
def makeRHSToSingleAttr(fdSet):
	tempSet = set()
	for fd in fdSet:
		if "," in fd[1]:
			rhsList = fd[1].split(',')
			for c in rhsList:
				tempSet.add((fd[0],c))
		else:
			tempSet.add(fd)

	return tempSet

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

# =================================== # 2. Elimate redundant attribute from LHS ===================================
def removeLhsRedundantAttr(fdSet):
	tempSet = set()
	for fd in fdSet:
		if ',' in fd[0]: # possible redundancy

			redundantAttr = set()
			for c in fd[0].split(','):
				templhs = fd[0].split(',')
				templhs.remove(c) #temporarily remove from LHS

				closure = getClosure(templhs, fdSet)
				if fd[1] in closure: # then we know that single attribute is redundant
					# print c + " is redundant in " + fd[0] + " --> " + fd[1]
					redundantAttr.add(c)
			
			lhs = fd[0].split(',')
			for c in redundantAttr: # we got a redundant values
				lhs.remove(c)
			
			tempSet.add((''.join(lhs), fd[1]))
				# check if we can get a closure that gets us the rhs
		else:
			tempSet.add(fd)

	if(fdSet == tempSet): # eliminated all redundant LHS attributes
		return tempSet
	else:
		return removeLhsRedundantAttr(tempSet)

# =================================== 3. Delete redundant FDs ===================================
def removeRedundantFds(fdSet):
	newFDSet = set()
	for fd in fdSet:
		tempFdSet = set(fdSet)
		tempFdSet.remove(fd)

		lhs = fd[0].split(',')
		closure = getClosure(lhs, tempFdSet)
		
		if not fd[1] in closure: # not redundant
			newFDSet.add(fd)

	if(fdSet == newFDSet): # if we have cleaned up all redundant!
		return newFDSet
	else:
		return removeRedundantFds(newFDSet)

def computeMinimalCover(conn, c):
	print "Computing minimal cover"

	# select the FDs table
	fdTableName = getFDTableName(conn, c)
	fdSet = getFDSet(conn, c, fdTableName)

	minimalCover = makeRHSToSingleAttr(fdSet)
	minimalCover = removeLhsRedundantAttr(minimalCover)
	minimalCover = removeRedundantFds(minimalCover)

	return minimalCover





