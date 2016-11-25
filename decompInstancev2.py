
from helpers import *
from mini_proj_2 import *
from databaseController import *
from schema3nf import *
import sqlite3
import sys


def getOutputSchemas(conn,c):
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'output_%' AND name NOT LIKE 'output_fds%';")
	result = c.fetchall()
	extractTitles = list()

	if not result:
		print "Error: could not get Output Schemas"
		exit()

	for r in result:
		extractTitles.append(r[0])
	return extractTitles

def decomposeInstance(conn,C):
	#the output tables already exist inside the db, regardless of whether they are 3nf or bcnf
	#simply take the instance data from  input_[name] and organize them among the decomposed output schemas
	# the tables/schemas already exist, just need to find the correct columns - inside the schema name- and use sql to 
	#extract and insert the corresponding values

	outputSchemas = getOutputSchemas(conn,C)
	print("OutputSchemas:",outputSchemas)

	C.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'input_%' AND name NOT LIKE 'input_fds%';")
	inputTable = C.fetchone()
	inputTable = inputTable[0]

	for s in outputSchemas:
		x,y,z= s.split('_')
		z = set(z)
		print("Schema",s,z)
		queryGetData= "SELECT " + getCommaString(z) + " FROM " + inputTable + ";"
		C.execute(queryGetData)
		values = C.fetchall()
		values = set(values)
		
		for v in values:
			questionMarks =  "?" * len(v)
			questionMarks = list(questionMarks)
			questionMarks = getCommaString(questionMarks)
			temp = list(v)
			print("V",temp)
			print(questionMarks)

			query = "INSERT INTO " + s + " VALUES " + "("+ questionMarks +")"
			C.execute(query,temp)

def main():
	conn,c=getConnectionCursor('MiniProject2-InputOutputExampleBCNF.db')
	getOutputSchemas(conn,c)
	decomposeInstance(conn,c)

	
main()
