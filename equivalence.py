from schema3nf import *
from databaseHelpers import *

def checkEquivalence(F,G):
	equiv = True
	for f in F:
		ac=getClosure(f[0],G)
		ac = getStringSet(ac)
		containsRHS = True
		for i in f[1]:
			if i not in ac:
				containsRHS = False
				break		

		if not containsRHS:
			equiv = False
			break

	return equiv


# def main():
# 	F = set([('A','C'),('A,C','D'),('E,A','D'),('E','F')])
# 	G = set([('A','C,D'),('E','A,D,F')])

# 	test = checkEquivalence(F,G)
# 	print(test)



# main()