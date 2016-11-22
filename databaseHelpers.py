import os.path
import re
import sqlite3
from schema3nf import *

def strStripLower(str):
	str = str.strip()
	str = str.lower()
	return str


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

def synthesizeTo3NF(conn, c):
	print "In synthesize 3NF"

	# returns a set of (LHS, RHS)
	minimalCover = computeMinimalCover(conn, c)
	partitionedSet = partitionSetToSameLHS(minimalCover)
	schema = formSchemaForEachUi(partitionedSet)
	addAdditionalSchemaIfNoSuperKey(conn, c, schema)


def decomposeToBCNF(conn, c):
	print "In decompose BCNF"
	








