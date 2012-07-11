# http://morepypy.blogspot.com/2010/05/efficient-and-elegant-regular.html
# https://codespeak.net/svn/user/cfbolz/hack/regex/regex.py

import logging
debug = logging.debug
logging.getLogger().setLevel(30) # debug

class Regex(object):
    def __init__(self, empty):
        # empty denotes whether the regular expression
        # can match the empty string
        self.empty = empty
        # mark that is shifted through the regex
        self.marked = False

    def reset(self):
        """ reset all marks in the regular expression """
        debug('resetting')
        self.marked = False

    def shift(self, c, mark):
        """ shift the mark from left to right, matching character c."""
        # _shift is implemented in the concrete classes
        debug('shifting')
        marked = self._shift(c, mark)
        self.marked = marked
        debug('got: %s', marked)
        return marked

def match(re, s):
    if not s:
        return re.empty
    # shift a mark in from the left
    result = re.shift(s[0], True)
    for c in s[1:]:
        # shift the internal marks around
        result = re.shift(c, False)
    re.reset()
    return result

class Char(Regex):
    def __init__(self, c):
        Regex.__init__(self, False)
        self.c = c

    def _shift(self, c, mark):
        return mark and c == self.c

class Epsilon(Regex):
    def __init__(self):
        Regex.__init__(self, empty=True)

    def _shift(self, c, mark):
        return False

class Binary(Regex):
    def __init__(self, left, right, empty):
        Regex.__init__(self, empty)
        self.left = left
        self.right = right

    def reset(self):
        self.left.reset()
        self.right.reset()
        Regex.reset(self)

class Alternative(Binary):
    def __init__(self, left, right):
        empty = left.empty or right.empty
        Binary.__init__(self, left, right, empty)

    def _shift(self, c, mark):
        marked_left  = self.left.shift(c, mark)
        marked_right = self.right.shift(c, mark)
        return marked_left or marked_right


class Repetition(Regex):
    def __init__(self, re):
        Regex.__init__(self, True)
        self.re = re

    def _shift(self, c, mark):
        return self.re.shift(c, mark or self.marked)

    def reset(self):
        self.re.reset()
        Regex.reset(self)

class Sequence(Binary):
    def __init__(self, left, right):
        empty = left.empty and right.empty
        Binary.__init__(self, left, right, empty)

    def _shift(self, c, mark):
        old_marked_left = self.left.marked
        marked_left = self.left.shift(c, mark)
        marked_right = self.right.shift(
            c, old_marked_left or (mark and self.left.empty))
        return (marked_left and self.right.empty) or marked_right

def make_regex(n):
    def a():
        return Char("a")
    def aorb():
        return Alternative(a(), Char("b"))
    def any():
        return Repetition(aorb())
    aorbn = aorb()
    for i in range(n - 1):
        aorbn = Sequence(aorb(), aorbn)
    return Sequence(Sequence(Sequence(Sequence(any(),  a()), aorbn), a()), any())

re = make_regex(20)
def main(args):
    import os
    chunks = []
    # use os.read to be RPython compatible
    while True:
        s = os.read(0, 4096)
        if not s:
            break
        chunks.append(s)
    s = "".join(chunks)
    print len(s)
    print match(re, s)
    return 0

# needed for PyPy translation toolchain
def target(*args):
    return main, None


def test_empty():
    re = Epsilon()
    assert match(re, "")
    re = Char("a")
    assert not match(re, "")

def test_char():
    re = Char("a")
    assert match(re, "a")
    assert not match(re, "b")


def test_alternative():
    re = Alternative(Char("a"), Char("b"))
    assert match(re, "a")
    assert match(re, "b")
    assert not match(re, "c")


def test_repetition():
    re = Repetition(Char("a"))
    for i in range(10):
        assert match(re, "a" * i)
    assert not match(re, "c")


def test_sequence():
    re = Sequence(Char("a"), Char("b"))
    assert match(re, "ab")
    assert not match(re, "aa")
    assert not match(re, "bb")
    assert not match(re, "a")
    assert not match(re, "b")
    assert not match(re, "c")
    assert not match(re, "")

def test_empty_or_a():
    re = Alternative(Epsilon(), Char("a"))
    assert match(re, "")
    assert match(re, "a")
    assert not match(re, "abc")

def test_make_regex():
    n = 5
    re = make_regex(5)
    import random
    match(re, "".join([random.choice(["a", "b"]) for i in range(n ** 2)]))

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))



