# Mini Project 2
import os.path
import re

def connectToInputDB():
	dbFile = raw_input("Please enter an input database (name.db): ")

	# check if file exits
	if (not os.path.isfile(dbFile)) and (not re.match(".+\\.db", dbFile)):
		print "Invalid filename, please try again!"
		connectToInputDB()

	print "Its a valid file..."


def main():
	print "Cmput 291: Mini Project 2"

	connectToInputDB()



if __name__ == '__main__':
	main()