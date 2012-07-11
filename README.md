# SEQUEX - regular expressions for other sequences



"""

runs = S(
    S({'someattr': 'somevalue'}).any(), S({'otherattr': 'othervalue'})
)


# as a regex:  x*y

# concepts:
#    grouping
#    count (one or more, zero or more, etc)
#    refernences?
#    greedy / non-greedy


"""


class S(object):
    pass



# So, what is a regex

(see http://swtch.com/~rsc/regexp/regexp1.html)

allowed:

    s[*+?]
    s|t
    st

precedence
    (weakest)

    alternation
    concatenation
    repetition
    parens

    (stongest)


NO backreferences!

(backreferences aren't pure re's and can require exponential cost)

