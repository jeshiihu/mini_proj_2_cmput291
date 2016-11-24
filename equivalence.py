from helpers import *

def checkEquivalence(F,G):
	#check if F is contained inside G 
	FG = 0
	for f in F:
		#check if each FD of F is entailed by G via calculating attribute closure
		ac=getClosure(f[0],G)
		ac = getStringSet(ac)

		containsRHS = 0
		#when checking if RHS is inside the resulting attribute closure, check each element individually
		for i in getStringSet(f[1]):
			if i not in ac:
				containsRHS+=1
		if containsRHS!=0:
			FG+=1

	GF = 0
	for g in G:
		ac=getClosure(g[0],F)
		ac = getStringSet(ac)
		hasRHS = 0
		for i in getStringSet(g[1]):
			if i not in ac:
				hasRHS+=1
		if hasRHS!=0:
			GF+=1


	if FG==0 and GF==0:
		return True
	else:
		return False		


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
		print('after add',fd,closure)
	if(lhs == closure): # we have iterated through the whole thing and cant add anymore!
		return getCommaString(closure)
	else:
		return getClosure(closure, fdSet)
