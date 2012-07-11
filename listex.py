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

	def search(self,indexable_list):
		L = indexable_list
		return Listex(anything).then(self).then(anything).match(L)

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
	assert Listex(dict(a=1)).then(dict(b=1)).search(mylist)

	assert not Listex(dict(a=1)).then(dict(b=1)).then({'not':'here'}).search(mylist)






