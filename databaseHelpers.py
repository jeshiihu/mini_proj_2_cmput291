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
	
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	result = c.fetchone()

	if not result: #tables haven't been created
		print "Reading tables..."
		scriptFile = open('p1-tables.sql', 'r')
		script = scriptFile.read()
		scriptFile.close()
		c.executescript(script)
		conn.commit()

	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	return conn, c

def synthesizeTo3NF(conn, c):
	print "In synthesize 3NF"

	# returns a set of (LHS, RHS)
	minimalCover = computeMinimalCover(conn, c)
	partitionedSet = partitionSetToSameLHS(minimalCover)
	
	for fd in partitionedSet: # keys = LHS
		print fd

def decomposeToBCNF(conn, c):
	print "In decompose BCNF"
	








