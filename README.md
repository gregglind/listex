# Listex -- regular expressions for other sequences

## Use Case

You have a list of objects (dictionaries, hashes, js objects), of which you
want some subset.  You would use a regular expression if these were strings,
but they aren't!

Let `listex` help!

Same great concepts you love from regexen, generalized out to match functions
over objects!

## Example

    >>> from listex import Listex, Some
    >>> mylist = [dict(x=1), dict(a=1,b=3), dict(x=1), dict(a=1,x=[1,2,3])]
    >>> print list(Listex(dict(a=1)).search(mylist))
    [(1, 2), (3, 4)]  # the listex matched at 1 and 3


## What exactly is Regular Expression?

(see http://swtch.com/~rsc/regexp/regexp1.html)

### allowed:

*    `s[*+?]`
*    `s|t`
*    `st`

### precedence

* (weakest)
* alternation
* concatenation
* repetition
* parens
* (stongest)


**NO backreferences!** backreferences aren't pure re's and can require exponential cost.


## TODO / Scope

* expose simple regular expressions over objects (grouping, counts, greedy/non-greedy)
* better 'chainable' language for listexen
* javascript implemention
* full test suite
* improve search implementation / runtime




