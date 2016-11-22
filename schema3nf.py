import sqlite3

def getCommaString(set):
	string = ""
	for c in set:
		string = string + c + ","

	while(1):
		if string[-1:] == ",":
			string = string[:-1]
		else:
			break

	return string

def getStringSet(string):
	return string.split(',')

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

	return fdSet

# =================================== 1. make the RHS of each FD into a single attribute ===================================
def makeRHSToSingleAttr(fdSet):
	tempSet = set()
	for fd in fdSet:
		if "," in fd[1]:
			rhsList = getStringSet(fd[1])
			for c in rhsList:
				tempSet.add((fd[0],c))
		else:
			tempSet.add(fd)

	return tempSet

def getClosure(lhs, fdSet):
	# working with sets, so no need to worry about duplicates
	closure = set(lhs) # eg. BH+ = BH

	for fd in fdSet: 
		tempLHS = getStringSet(fd[0])
		foundLHS = True

		for c in tempLHS:	# find if we can add the RHS to the closure
			if c not in closure:
				foundLHS = False
				break

		if foundLHS: # we can add it!
			closure.add(fd[1])

	if(lhs == closure): # we have iterated through the whole thing and cant add anymore!
		return getCommaString(closure)
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
					redundantAttr.add(c)
			
			lhs = getStringSet(fd[0])
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

	minCover = set()
	for fd in minimalCover:
		minCover.add((getCommaString(fd[0]), fd[1]));

	return minCover

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
		RiList = list() # set of attributes
		for fd in fds:
			for attr in fd: # add all attributes to the Ri
				if attr not in RiList:
					RiList.append(attr)

		Ri = ''.join(RiList)
		Ri = Ri.replace(',', '')
		newSchema[Ri] = fds # fds is the Ui

	return newSchema


# ====================== 4. If none of the schemas from step 2 includes a superkey for R, add another relation schema that 
# ====================== has a key for R
def addAdditionalSchemaIfNoSuperKey(conn, c, schema, minimalCover):
	print "adding additional schema if necessary"
	tableName = getInputTableName(conn, c)
	results = getInputTable(conn, c, tableName)
	keys = results[0].keys()

	foundSuperKey = False
	prevClosure = ""
	lhsWithMostAttributesInClosure = ""
	for fd in minimalCover:
		closure = getClosure(fd[0], minimalCover) # this is a comma string
		allAttrInKeys = True

		for attr in keys:
			if attr not in closure:
				if(len(closure) >= len(prevClosure)): # get the closure that has the most attributes!
					lhsWithMostAttributesInClosure = fd[0]
					prevClosure = closure

				allAttrInKeys = False
				break

		if allAttrInKeys:
			foundSuperKey = True
			break

	if foundSuperKey: # don't need to add an additional schema
		return

	#augmentation
	closure = getClosure(lhsWithMostAttributesInClosure, minimalCover)
	lhs = getStringSet(lhsWithMostAttributesInClosure)
	for attr in keys:
		if attr not in closure: # add to the lhs
			lhs.append(attr)

	for min in minimalCover:
		print min

	lhs = ''.join(lhs)
	newSchema = dict()
	newSchema[lhs] = ""
	return newSchema

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


def createFDTables(conn, c, schemaDict, baseOutputName):
	for key in schemaDict:
		# create the output FDs tables
		fdTableName = baseOutputName + key
		dropTable(conn, c, fdTableName)
		query = "CREATE TABLE " + fdTableName + " (LHS TEXT, RHS TEXT);"
		c.execute(query)
		for fd in schemaDict[key]:
			insert = [fd[0], fd[1]] #lhs rhs
			query = "INSERT INTO " + fdTableName + " VALUES (?,?)"
			c.execute(query, insert)
		conn.commit()

def createRelationalTables(conn, c, schemaDict, baseOutputName):
	for key in schemaDict:
		tableName = baseOutputName + key
		dropTable(conn, c, tableName)
		query = "CREATE TABLE " + tableName + " (LHS TEXT, RHS TEXT);"
		c.execute(query)

def createTables(conn, c, schemaDict): # format is a dict
	inputTableName = getInputTableName(conn, c)
	outputTableName = inputTableName.replace("Input", "Output") + "_"

	inputFdTableName = getFDTableName(conn, c)
	outputFdTableName = inputFdTableName.replace("Input", "Output") + "_"

	input = getInputTable(conn, c, inputTableName)

	print "keys", input[0].keys()
	for i in input:
		print i

	createRelationalTables(conn, c, schemaDict, outputTableName)
	createFDTables(conn, c, schemaDict, outputFdTableName)







