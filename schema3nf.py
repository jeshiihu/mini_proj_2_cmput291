import sqlite3

def getInputTableName(conn,c):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'input_%' AND name NOT LIKE 'input_fds_%';")
	result = c.fetchone()

	if not result:
		print "Error: could not get Input Table Name"
		exit()

	return result[0]

def getInputTable(conn, c, tablename):
	query = 'SELECT * FROM ' + tablename + ';'
	c.execute(query)
	results = c.fetchall()

	if not results:
		print "Error: could not get Input Table Name"
		exit()

	return results

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

# ====================== 1. Compute Fm, the minimal cover for F
def computeMinimalCover(conn, c):
	print "Computing minimal cover"

	# select the FDs table
	fdTableName = getFDTableName(conn, c)
	fdSet = getFDSet(conn, c, fdTableName)

	minimalCover = makeRHSToSingleAttr(fdSet)
	minimalCover = removeLhsRedundantAttr(minimalCover)
	minimalCover = removeRedundantFds(minimalCover)

	return minimalCover

# ====================== 2. Partition U into sets U1, U2, ... Un such that the LHS of all elements of Ui are the same.
def partitionSetToSameLHS(minimalCover):
	print "partition to same LHS"
	newFD = set()
	for fd in minimalCover:
		singleFDSet = set()
		tempSet = set(minimalCover)
		tempSet.remove(fd)

		singleFDSet.add(fd)
		for tempFD in tempSet:
			if(fd[0] == tempFD[0]): # we found another same LHS
				singleFDSet.add(tempFD)

		newFD.add(frozenset(singleFDSet))

	return newFD

# ====================== 3. For each Ui form schema Ri = (Ri, Ui), where Ri is the set of all attributes mentioned in Ui,
# ====================== each FD of U will be in some Ri. Hence the decomposition is dependency preserving.
def formSchemaForEachUi(partitionedSet):
	print "forming schema for each UI"
	newSchema = dict()
	fdSet = set()

	for fds in partitionedSet:
		RiSet = set() # set of attributes
		for fd in fds:
			for attr in fd: # add all attributes to the Ri
				RiSet.add(attr)

		newSchema[''.join(RiSet)] = fds # fds is the Ui

	for schema in newSchema:
		print schema, newSchema[schema]

	return newSchema


# ====================== 4. If none of the schemas from step 2 includes a superkey for R, add another relation schema that 
# ====================== has a key for R
def addAdditionalSchemaIfNoSuperKey(conn, c, schema, minimalCover):
	print "adding additional schema if necessary"
	tableName = getInputTableName(conn, c)
	results = getInputTable(conn, c, tableName)
	keys = results[0].keys()

	foundSuperKey = False
	for fd in minimalCover:
		print fd[0] + '-->' + fd[1]
		closure = getClosure(fd[0], minimalCover)
		# print "Closure for ", fd[0] + "+ = ", closure
		allAttrInKeys = True

		for attr in keys:
			if attr not in closure:
				allAttrInKeys = False
				break

		if allAttrInKeys:
			foundSuperKey = True
			break

	if foundSuperKey: # don't need to add an additional schema
		return

	# must add an additional schema
	print "idk how to do this.."

def tableExists(conn, c, tableName):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (tableName,))
	result = c.fetchone()

	if not result:
		return False

	return True

def dropTable(conn, c, tableName):
	query = "DROP TABLE IF EXISTS " + tableName + ";"
	c.execute(query)
	conn.commit()


def createTables(conn, c, schemaDict): # format is a dict
	inputTableName = getInputTableName(conn, c)
	outputTableName = inputTableName.replace("Input", "Output") + "_"

	inputFdTableName = getFDTableName(conn, c)
	outputFdTableName = inputFdTableName.replace("Input", "Output") + "_"


	for key in schemaDict:
		tableName = outputTableName + key
		print tableName

		fdTableName = outputFdTableName + key
		
		dropTable(conn, c, fdTableName)
		query = "CREATE TABLE " + fdTableName + " (LHS TEXT, RHS TEXT);"
		c.execute(query)
		conn.commit()







