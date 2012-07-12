"""

M = oneormore({'key': 'a'}).then({'some':'thing','other':'thing'})

mylist=[]
M.match(mylist)

?  listex({'a':1}).many().then(lambda x: x['a'] in [1,2,3]).some(3,5)
"""

import regex


# based heavily on regex.Char
class Objlike(regex.Regex):
	def __init__(self,pattern):
		regex.Regex.__init__(self,False)
		if callable(pattern):
			self.pattern_fn = pattern
		else:
			self.pattern_fn = lambda (obj): all(obj.get(k,None) == v for k,v in pattern.iteritems())

	def _shift(self,c,mark):
		return mark and self.pattern_fn(c)


def anything(*args,**kwargs):  
	return True

class Listex(object):
	def __init__(self,pattern_or_callable):
		"""
		Args:
			pattern_or_callable:  to be applied on each 
				item in the iterable.  
		"""
		if isinstance(pattern_or_callable,regex.Regex):
			self.regex =  pattern_or_callable
		else:
			self.regex = Objlike(pattern_or_callable)


	def then(self,other):
		""" promotes the 'other' regex into Sequence by side effect 

		Args:
			other - another listex

		Returns:
			self
		"""
		if not isinstance(other,Listex):
			try:
				other = Listex(other)
			except:
				raise TypeError("other must be Listex or Listexable")

		self.regex = regex.Sequence(self.regex,other.regex)
		return self


	def match(self,indexable_list):
		# due to limitations in regex.match, this must be indexable
		# i.e., not just iterable
		return regex.match(self.regex, indexable_list)

	def search(self,indexable_list,start=0):
		L = indexable_list
		#return Listex(anything).then(self).then(anything).match(L)
		# we can get positions O(logN), by
		# binary serarching both halves of L
		# then matching on that.
		n = len(L)
		"""
		until I figure out how to find 'end of match'
	    ## ugh, this is O(n**3 * m)!

		idea:
			if self.then(anything).match(L):
				# start cutting from right,
			else:
				# cut from left

		"""
		lastmatch=0
		for left in range(n):
			if left < lastmatch:
				continue # ugh, primitive
			for right in xrange(n,left,-1):  # trim right
				if self.match(L[left:right]):
					lastmatch = right # where to start next
					yield True, start+left,start+right
					#for x in self.search(L[left:],start=left):
					#	yield x
					break


class Some(Listex):
	def __init__(self,pattern_or_callable,min=0,max=0):
		poc = pattern_or_callable
		if max != 0:
			raise ValueError ("max not yet implemented")
		if min > 0:
			Listex.__init__(self,pattern_or_callable)
			for ii in xrange(min-1):
				self.then(Listex(pattern_or_callable))

			self.then(Listex(regex.Repetition(Objlike(poc))))
		else:
			Listex.__init__(self,regex.Repetition(Objlike(poc)))

class oneormore(Listex):
	pass

class zeroone(Listex):
	pass

class zeroormore(Listex):
	pass


def test_me():
	""" various tests, lumped together ."""
	mylist = [dict(a=1,b=2),dict(c=1),dict(d=3,)]

	mylist = [dict(a=1)]
	assert Listex(dict(a=1)).match(mylist)

	assert not Listex(dict(a=2)).match(mylist) 

	assert not Listex(dict(a=2)).then(dict(b=1)).match(mylist)

	# 
	assert regex.match(regex.Sequence(Objlike(dict(a=1)),Objlike(dict(b=2))),[dict(a=1),dict(b=2)])

	mylist = [dict(a=1),dict(b=2,c=3)]
	assert Listex(dict(a=1)).then(dict(b=2)).match(mylist)

	# search
	mylist = [dict(d=[3,4,5]),dict(a=1),dict(b=1,c=2),dict(d=[1,2,3])]
	assert not Listex(dict(a=1)).then(dict(b=1)).match(mylist)
	#assert Listex(dict(a=1)).then(dict(b=1)).search(mylist)

	#assert not Listex(dict(a=1)).then(dict(b=1)).then({'not':'here'}).search(mylist)


	mylist = [dict(x=1), dict(a=1), dict(x=1), dict(a=1)]
	print list(Listex(dict(a=1)).search(mylist))


	mylist = [dict(x=1), dict(a=1), dict(a=1),dict(a=1), dict(x=1), dict(a=1)]
	print list(Listex(regex.Repetition(Objlike(dict(a=1)))).search(mylist))

	print list(Some(dict(a=1),2).search(mylist))
