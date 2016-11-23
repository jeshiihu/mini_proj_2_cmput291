from schema3nf import *
from helpers import *

def checkEquivalence(F,G):
	FG = 0
	for f in F:
		ac=getClosure(f[0],G)
		ac = getStringSet(ac)
		#print(str(f[0])+','+str(ac))
		containsRHS = 0
		for i in f[1]:
			if i not in ac:
				containsRHS+=1
		if containsRHS!=0:
			FG+=1


	GF = 0
	for g in G:
		ac=getClosure(g[0],F)
		ac = getStringSet(ac)
		print(str(g[0])+','+str(ac))

		hasRHS = 0
		for i in g[1]:
			if i not in ac:
				hasRHS+=1
		if hasRHS!=0:
			GF+=1

	print(FG)
	print(GF)	

	if FG==0 and GF==0:
		return True
	else:
		return False		
	


	


def main():
	F = set([('A','C'),("A,C",'D'),('E','A,D'),('E','F')])
	G = set([('A',"C,D"),('E',"A,D,F")])

	test = checkEquivalence(F,G)
	print(test)



main()