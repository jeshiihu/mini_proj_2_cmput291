import os.path
import re
import sqlite3
from schema3nf import *
from helpers import *
import copy

def getDBFile():
	dbFile = raw_input("Please enter an input database (name.db): ")
	dbFile = strStripLower(dbFile)

	# check if file exits
	if dbFile == "-quit":
		exit()

	if not os.path.isfile(dbFile) or not re.match(".+\\.db", dbFile):
		print "Invalid filename, please try again!"
		getDBFile()

	return dbFile

def getConnectionCursor(filename):
	conn = sqlite3.connect(filename) 
	conn.text_factory = str
	c = conn.cursor()
	c.execute('PRAGMA foreign_keys=ON;')

	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	return conn, c

def findClosure(conn, c):
	print "Finding Closure"


def synthesizeTo3NF(conn, c):
	print "In synthesize 3NF"

	# returns a set of (LHS, RHS)
	minimalCover = computeMinimalCover(conn, c)
	partitionedSet = partitionSetToSameLHS(minimalCover)
	schema = formSchemaForEachUi(partitionedSet)
	newRiDict = addAdditionalSchemaIfNoSuperKey(conn, c, minimalCover)

	createTables(conn, c, schema)

	inputTableName = getInputTableName(conn, c)
	outputTableName = inputTableName.replace("Input", "Output") + "_"
	createRelationalTables(conn, c, newRiDict)


def decomposeToBCNF(conn, c):
	print "decomposing to BCNF"
	sqlGetRTable = '''
				SELECT name
				 FROM sqlite_master 
				 WHERE type='table' AND name LIKE 'input_%' AND name NOT LIKE 'input_fds_%';
				'''
	c.execute(sqlGetRTable)
	Rtable = c.fetchone()
	sqlGetR = '''
			select *
			from %s;
			'''
	c.execute(sqlGetR %Rtable[0])
	row = c.fetchone()
	Rsql = row.keys()
	R = ''
	for attribute in Rsql:
		R = R + attribute
	print(R)

	getTableColumnAndType(c, Rtable)

	sqlGetFTable = '''
			SELECT name 
			FROM sqlite_master 
			WHERE type='table' AND name LIKE 'input_fds_%';
			'''
	c.execute(sqlGetFTable)
	Ftable = c.fetchone()
	sqlGetF = '''
			select *
			from %s;
			'''
	c.execute(sqlGetF %Ftable[0])
	F = c.fetchall()
	print(F)

	BCNFR = []
	BCNFFD = []
	F2 = copy.copy(F)
	R2 = copy.copy(R)

	F1 = findViolatingBCNF(R2,F2)
	if (F1 == 'no violating'):
		print('already in BCNF')
		for R in R2:
			BCNFR.append(('',R))
		for FD in F2:
			BCNFFD.append(FD)
	else :
		print('Not in BCNF')
		while (1) :
			F1 = findViolatingBCNF(R2,F2)
			if (F1 == 'no violating'):
				BCNFR.append(('',R2))
				break
			if not F2:
				BCNFR.append(R2)
				break

			LHS = F1[0]
			RHS = F1[1]
			R1 = LHS.replace(',','') + RHS.replace(',','')
			BCNFR.append((LHS,R1))
			BCNFFD.append(F1)
			for attribute in RHS:
				if attribute in R:
					R2 = R2.replace(attribute, '')
			F2.remove(F1)
			for FD in F2:
				FDLHS = FD[0].replace(',','') 
				FDRHS = FD[1].replace(',', '')
				for RHSattribute in RHS:
					if (RHSattribute in FDLHS):
						F2.remove(FD)
						break
					if(RHSattribute in FDRHS):
						index = F2.index(FD)
						F2.remove(FD)
						if (FD[1].replace(RHSattribute,'') == ''):
							break
						else:
							F2.insert(index, (FD[0], FD[1].replace(RHSattribute,'')))
	print('******************************************************************************************')
	print('My Rs are: ',  BCNFR)
	print('my Fds are: ', BCNFFD)
	print(findDependencyPreserving(F, BCNFFD))
	createBCNFTables(conn, c, BCNFR, BCNFFD)


def findDependencyPreserving (F, Fprime):
	if(all(FD in Fprime for FD in F)):
		return 'is dependency preserving'
	allClosures = findAllClosures(Fprime)
	preserved = True
	for FD in F:
		LHSFD = FD[0].replace(',', '')
		RHSFD = FD[1].replace(',', '')
		for FDprime in Fprime:
			LHSFDprime = FDprime[0]
			RHSFDprime = FDprime[1]
			if((LHSFD == LHSFDprime) and (all(attribute in RHSFDprime for attribute in RHSFD))):
				break
			preserved = False
	if (preserved == False):
		return 'is NOT dependency preserving'
	return 'is dependency preserving'
	

def findAllClosures(F):
	allClosures = []
	for FD in F:
		LHS = FD[0]
		enclosure = LHS.replace(',', '')
		RHS = FD[1]
		otherF = copy.copy(F)
		otherF.remove(FD)
		closure = (LHS + RHS).replace(',','')
		foundViolatingFD = False;
		while (foundViolatingFD == False):
			old = closure
			for otherFD in otherF:
				otherFDLHS = otherFD[0].replace(',', '')
				if(all(attribute in closure for attribute in otherFDLHS)):
					otherFDRHS = otherFD[1].replace(',', '')
					for addAttribute in otherFDRHS:
						for attribute in addAttribute:
							if (attribute not in closure):
								closure = closure + attribute
			if (old == closure):
				break
		allClosures.append((enclosure, closure))
	return allClosures

def findViolatingBCNF (R, F):
	for FD in F:
		LHS = FD[0]
		RHS = FD[1]
		otherF = copy.copy(F)
		otherF.remove(FD)
		closure = (LHS + RHS).replace(',','')
		foundViolatingFD = False;
		while (foundViolatingFD == False):
			old = closure
			for otherFD in otherF:
				otherFDLHS = otherFD[0].replace(',', '')
				if(all(attribute in closure for attribute in otherFDLHS)):
					otherFDRHS = otherFD[1].replace(',', '')
					for addAttribute in otherFDRHS:
						for attribute in addAttribute:
							if (attribute not in closure):
								closure = closure + attribute
			if (old == closure):
				if(all(attribute in closure for attribute in R)):
					break
				else:
					return FD
					foundViolatingFD = True
	return 'no violating'

def createBCNFFDTables(conn, c, F):
	inputFdTableName = getFDTableName(conn, c)
	baseOutputName = inputFdTableName.replace("Input", "Output") + "_"

	for FD in F:
		# create the output FDs tables
		Relation = FD[0].replace(',','') + FD[1].replace(',','')
		fdTableName = baseOutputName + ''.join(Relation)
		dropTable(conn, c, fdTableName)
		query = "CREATE TABLE " + fdTableName + " (LHS TEXT, RHS TEXT);"
		#print(query)
		c.execute(query)
		insert = [FD[0], FD[1]] #lhs rhs
		query = "INSERT INTO " + fdTableName + " VALUES (?,?)"
		c.execute(query, insert)
		conn.commit()

def createBCNFRelationalTables(conn, c, R):
	inputTableName = getInputTableName(conn, c)
	baseOutputName = inputTableName.replace("Input", "Output") + "_"
	
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (inputTableName, ))
	result = c.fetchone()
	tableInfo = getTableColumnAndType(c, result)

	for Relation in R:
		if (Relation[0] != ''):
			key = Relation[1]
			columns = ""
			tableName = baseOutputName + ''.join(key)
			for attr in key:
				columnType = getSpecificColumnType(tableInfo, attr)
				columns = columns + attr + " " + columnType + ', '
			primaryKey = Relation[0]
			columns = columns + "PRIMARY KEY (" + primaryKey + ")"
			columns = strStripUpper(columns)
			dropTable(conn, c, tableName)
			query = "CREATE TABLE " + tableName + "(" + columns + ");"
			#print(query)
			c.execute(query)
			conn.commit()

		else:
			key = Relation[1]
			columns = ""
			tableName = baseOutputName + ''.join(key)
			for attr in key:
				columnType = getSpecificColumnType(tableInfo, attr)
				columns = columns + attr + " " + columnType + ', '
			columns = strStripUpper(columns)
			dropTable(conn, c, tableName)
			query = "CREATE TABLE " + tableName + "(" + columns + ");"
			c.execute(query)
			conn.commit()

	conn.commit()

def createBCNFTables(conn, c, R, F): # format is a dict
	createBCNFRelationalTables(conn, c, R)
	createBCNFFDTables(conn, c, F)
