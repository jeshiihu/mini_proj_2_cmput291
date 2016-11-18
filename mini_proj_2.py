# Mini Project 2
import sqlite3

from databaseHelpers import *

def promptAction(conn, c):
	print "Please select an action you wish to perform..."
	print "	[0] Synthesize table to 3NF"
	print "	[1] Decompose table to BCNF"
	print "	[-quit] Quit program"
	action = raw_input("action: ")

	if(action == str(0)):
		synthesizeTo3NF(conn, c)
	elif(action == str(1)):
		decomposeToBCNF(conn, c)
	elif(action == "-quit"):
		exit()
	else:
		print "Invalid action. Please try again!"
		promptAction(conn, c)

def main():
	print "Welcome to the Cmput 291: Mini Project 2!"

	filename = getDBFile()
	conn, c = getConnectionCursor(filename)

	promptAction(conn, c)



if __name__ == '__main__':
	main()