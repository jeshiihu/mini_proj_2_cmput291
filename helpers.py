# helpers

#strips a string and lowercases it
def strStripLower(str):
	str = str.strip()
	str = str.lower()

	return str

def strStripUpper(str):
	str = str.strip()
	str = str.upper()

	while(1):
		if str[-1:] == ",":
			str = str[:-1]
		else:
			break

	return str

#takes in a set of objs (chars) and returns it in string form
# Example: set ['A', 'B', 'C'], returns "A,B,C"
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

# takes in a string (should be used with a comma seperated string), and splits it up into a set
# Example: "A,B,C", returns set ['A', 'B', 'C']
def getStringSet(string):
	return set(string.split(','))

# Gets the Relational table name (to be used when decomposing into BCNF and 3NF)
def getInputTableName(conn,c):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'input_%' AND name NOT LIKE 'input_fds_%';")
	result = c.fetchone()

	if not result:
		print "Error: could not get Input Table Name"
		exit()

	return result[0]

# Gets table content of any table
def getInputTable(conn, c, tablename):
	query = 'SELECT * FROM ' + tablename + ';'
	c.execute(query)
	results = c.fetchall()

	if not results:
		print "Error: could not get Input Table Name"
		exit()

	return results

# Gets the Functional dependency table name (to be used when decomposing into BCNF and 3NF)
def getFDTableName(conn, c):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'input_fds_%';")
	result = c.fetchone()

	if not result:
		print "Error: could not get Functional Dependancy Table Name"
		exit()

	return result[0]

# From the Fds Table and returns a set of tuples, fd[0] = LHS, fd[1] = RHS
# Example return (("B,H", "C"), ("C", "D"), ("A", "B"))
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

# gets the table info
def getTableColumnAndType(c, table):
	sqltest = '''
				select sql from sqlite_master
				where tbl_name = '%s' and type = 'table'
				'''
	c.execute(sqltest %table[0])
	tableInfo = c.fetchall()

	if not tableInfo:
		print "Error, cannot get table info"
		exit()

	tableInfo = tableInfo[0][0]
	tableInfo = tableInfo.replace('CREATE TABLE %s(' %table[0], '')
	tableInfo = tableInfo.replace(')', '')
	tableInfo = tableInfo.replace('\n', '')
	tableInfo = tableInfo.rstrip().strip().lstrip()

	return tableInfo

# returns a string indicating the type, column
def getSpecificColumnType(allColumns, column):
	if column not in allColumns:
		print "Error column " + column + " not found"
		exit()

	setOfColumnsAndTypes = getStringSet(allColumns)
	for columnType in setOfColumnsAndTypes:
		columnType = columnType.strip()
		singleColumnType = tuple(columnType.split(" "))
		if column == singleColumnType[0]:
			return singleColumnType[1]


def tableExists(conn, c, tableName):
	tableName = strStripLower(tableName)
	tableName = tableName.replace(" ", "")
	query = "SELECT * FROM " + tableName + ";"
	c.execute(query)
	result = c.fetchone()

	if not result:
		return False

	return True

def dropTable(conn, c, tableName):
	query = "DROP TABLE IF EXISTS " + tableName + ";"
	c.execute(query)
	conn.commit()

def getClosure(lhs, fdSet):
	# working with sets, so no need to worry about duplicates
	closure = set(lhs) # eg. BH+ = BH
	#if LHS has more than one attribute, comma will be added during set transformation so remove it
	if ',' in closure:
		closure.remove(',')

	for fd in fdSet: 
		tempLHS = getStringSet(fd[0])
		foundLHS = True

		for c in tempLHS:	# find if we can add the RHS to the closure
			if c not in closure:
				foundLHS = False
				break

		if foundLHS: # we can add it!
			#split the RHS before adding so the values inside the set are of single attributes 
			splitRHS=getStringSet(fd[1])
			closure.update(splitRHS)
			
	if(lhs == closure): # we have iterated through the whole thing and cant add anymore!
		return getCommaString(closure)
	else:
		return getClosure(closure, fdSet)




