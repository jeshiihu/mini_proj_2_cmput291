import sqlite3
from helpers import *

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
		RiSet = set() # set of attributes
		for fd in fds:
			for attr in fd: # add all attributes to the Ri
				for c in getStringSet(attr):
					if c not in RiSet:
						RiSet.add(c)
		newSchema[frozenset(RiSet)] = fds # fds is the Ui

	return newSchema

# ====================== 4. If none of the schemas from step 2 includes a superkey for R, add another relation schema that 
# ====================== has a key for R
def removeLhsSuperKey(keys, fdSet, lhs): #lhs is a set
	redundantAttr = set()

	for attr in lhs:
		tempLhs = set(lhs)
		tempLhs.remove(attr)
		closure = getClosure(tempLhs, fdSet)

		redundant = True
		for k in keys:
			if k not in closure: # then we know its not redundant
				redundant = False
				break

		if redundant:
			redundantAttr.add(attr)

	newLhs = set(lhs)
	for attr in redundantAttr:
		newLhs.remove(attr)

	if newLhs == lhs:
		return lhs
	else:
		return removeLhsSuperKey(keys, fdSet, newLhs)


def addAdditionalSchemaIfNoSuperKey(conn, c, minimalCover):
	print "adding additional schema if necessary"
	tableName = getInputTableName(conn, c)
	results = getInputTable(conn, c, tableName)
	keys = results[0].keys()

	foundSuperKey = False
	prevClosure = ""
	lhsWithMostAttributesInClosure = ""
	rhs = ""

	for fd in minimalCover:
		closure = getClosure(fd[0], minimalCover) # this is a comma string
		allAttrInKeys = True

		for attr in keys:
			if attr not in closure:
				if(len(closure) >= len(prevClosure)): # get the closure that has the most attributes!
					lhsWithMostAttributesInClosure = fd[0]
					rhs = fd[1]
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
	# print lhsWithMostAttributesInClosure + "+ = " + closure
	lhs = set(getStringSet(lhsWithMostAttributesInClosure))


	for attr in keys:
		if attr not in closure:
			lhs.add(attr)

	# print ''.join(lhs)
	newLhs = removeLhsSuperKey(keys, minimalCover, lhs)
	# print ''.join(newLhs)
	
	d = dict()
	d[frozenset(newLhs)] = ""
	return d

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


def createFDTables(conn, c, schemaDict):
	inputFdTableName = getFDTableName(conn, c)
	baseOutputName = inputFdTableName.replace("Input", "Output") + "_"

	for key in schemaDict:
		# create the output FDs tables
		fdTableName = baseOutputName + ''.join(key)
		dropTable(conn, c, fdTableName)
		query = "CREATE TABLE " + fdTableName + " (LHS TEXT, RHS TEXT);"
		c.execute(query)
		for fd in schemaDict[key]:
			insert = [fd[0], fd[1]] #lhs rhs
			query = "INSERT INTO " + fdTableName + " VALUES (?,?)"
			c.execute(query, insert)
		conn.commit()

def createRelationalTables(conn, c, schemaDict):
	inputTableName = getInputTableName(conn, c)
	baseOutputName = inputTableName.replace("Input", "Output") + "_"
	
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (inputTableName, ))
	result = c.fetchone()
	tableInfo = getTableColumnAndType(c, result)

	for key in schemaDict:
		columns = ""
		tableName = baseOutputName + ''.join(key)
		for attr in key:
			columnType = getSpecificColumnType(tableInfo, attr)
			columns = columns + attr + " " + columnType + ', '

		if len(schemaDict[key]) > 0: # as long as it has FDs
			fd = set(schemaDict[key]).pop()
			columns = columns + "PRIMARY KEY (" + fd[0] + ")"
		columns = strStripUpper(columns)
		dropTable(conn, c, tableName)
		query = "CREATE TABLE " + tableName + "(" + columns + ");"
		c.execute(query)
		conn.commit()

	conn.commit()

def createTables(conn, c, schemaDict): # format is a dict
	createRelationalTables(conn, c, schemaDict)
	createFDTables(conn, c, schemaDict)







