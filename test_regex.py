import unittest
from matchtester import MatchTester


class MatcherTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass


	def testMatches(self):
		for regex, canidate, expectedRes in tests:
			with self.subTest():
				try:
					matcher = MatchTester(regex)
				except Exception as e:
					self.fail('{}\n\t regex:	{}'.format(str(e), regex))
				res = matcher.matches(canidate)
				self.assertEqual(res, expectedRes, '\n\tregex:    {}\n\tcanidate: {}\n\texpected: {},\n\tactual:   {}'.format(regex, canidate, expectedRes, res))

	def testRepeatedUse(self):
		prev_regex = None
		matcher = None
		for regex, canidate, expectedRes in tests:
			with self.subTest():
				if regex != prev_regex:
					try:
						matcher = MatchTester(regex)
					except Exception as e:
						self.fail('{}\n\t regex:	{}'.format(str(e), regex))
				prev_regex = regex
				# run twice
				res = matcher.matches(canidate)
				self.assertEqual(res, expectedRes, '\n\tregex:    {}\n\tcanidate: {}\n\texpected: {},\n\tactual:   {}'.format(regex, canidate, expectedRes, res))
				res = matcher.matches(canidate)
				self.assertEqual(res, expectedRes, '\n\tregex:    {}\n\tcanidate: {}\n\texpected: {},\n\tactual:   {}'.format(regex, canidate, expectedRes, res))



tests = [
	('a', 'a', True),
	('a', 'b', False),
	('^abcd$', 'abcd', True),
	('^abcd$', 'abc', False),
	('^abc$', 'abcd', False),
	('^abcd$', 'bcd', False),
	('^bcd$', 'abcd', False),
	('a*', 'a', True),
	('a*', 'aaaa', True),
	('a*', '', True),
	('a*', 'b', True),
	('a*b', 'aaaab', True),
	('^(a|b|c)$', 'a', True),
	('^(a|b|c)$', 'b', True),
	('^(a|b|c)$', 'c', True),
	('^(a|b|c)$', 'd', False),
	('^(a|b|c)$', 'ab', False),
	('car|boat|jet', 'ab', False),
	('car|boat|jet', 'caoaret', False),
	('car|boat|jet', 'car', True),
	('car|boat|jet', 'boat', True),
	('car|boat|jet', 'jet', True),
	('^((abc)+)$', 'abc', True),
	('^((abc)+)$', 'abcabc', True),
	('^((abc)+)$', 'abcabcabc', True),
	('^((abc)+)$', 'abcabcab', False),
	('^((abc)+)$', 'abcabcaba', False),
	('^((abc)+)$', '', False),
	('^((abc)*)$', '', True),
	('^((abc)?)$', '', True),
	('^((abc)?)$', 'abc', True),
	('^(abc)?$', 'z', False),
	('^((a*)*)$', 'a', True),
	('^((a*)*)$', 'b', False),
	('^abc','abcd', True),
	('^bcd','abcd', False),
	('^bcd$','bcd', True),
	('^bcd$','bcde', False),
	('','sdgsa', True),
	('','', True),
	('^$','', True),
	('^$','a', False),


    ('', '', True),
    ('abc', 'abc', True),
    ('abc', 'xbc', False),
    ('abc', 'axc', False),
    ('abc', 'abx', False),
    ('abc', 'xabcy', True),
    ('abc', 'ababc', True),
    ('ab*c', 'abc', True),
    ('ab*bc', 'abc', True),
    ('ab*bc', 'abbc', True),
    ('ab*bc', 'abbbbc', True),
    ('ab+bc', 'abbc', True),
    ('ab+bc', 'abc', False),
    ('ab+bc', 'abq', False),
    ('ab+bc', 'abbbbc', True),
    ('ab?bc', 'abbc', True),
    ('ab?bc', 'abc', True),
    ('ab?bc', 'abbbbc', False),
    ('ab?c', 'abc', True),
    ('^abc$', 'abc', True),
    ('^abc$', 'abcc', False),
    ('^abc', 'abcc', True),
    ('^abc$', 'aabc', False),
    ('abc$', 'aabc', True),
    ('^', 'abc', True),
    ('$', 'abc', True),
    ('ab|cd', 'abc', True),
    ('ab|cd', 'abcd', True),
    ('()ef', 'def', True),
    ('((a))', 'abc', True),
    ('(a)b(c)', 'abc', True),
    ('a+b+c', 'aabbabc', True),
    ('(a+|b)*', 'ab', True),
    ('(a+|b)+', 'ab', True),
    ('(a+|b)?', 'ab', True),
    ('abc', '', False),
    ('a*', '', True),
    ('a|b|c|d|e', 'e', True),
    ('(a|b|c|d|e)f', 'ef', True),
    ('abcd*efg', 'abcdefg', True),
    ('ab*', 'xabyabbbz', True),
    ('ab*', 'xayabbbz', True),
    ('(ab|cd)e', 'abcde', True),
    ('^(ab|cd)e', 'abcde', False),
    ('(abc|)ef', 'abcdef', True),
    ('(a|b)c*d', 'abcd', True),
    ('(ab|ab*)bc', 'abc', True),
    ('(ab|a)b*c', 'abc', True),
    ('((a)(b)c)(d)', 'abcd', True),
    ('(((((((((a)))))))))', 'a', True),
    ('multiple words of text', 'uh-uh', False),
    ('multiple words', 'multiple words, yeah', True),
    ('(a)(b)c|ab', 'ab', True),
    ('(a)+x', 'aaax', True),
    ('(a)+b|aac', 'aac', True),
    ('abc', 'abc', True),
    ('abc', 'xbc', False),
    ('abc', 'axc', False),
    ('abc', 'abx', False),
    ('abc', 'xabcy', True),
    ('abc', 'ababc', True),
    ('ab*c', 'abc', True),
    ('ab*bc', 'abc', True),
    ('ab*bc', 'abbc', True),
    ('ab*bc', 'abbbbc', True),
    ('ab+bc', 'abbc', True),
    ('ab+bc', 'abc', False),
    ('ab+bc', 'abq', False),
    ('ab+bc', 'abbbbc', True),
    ('ab?bc', 'abbc', True),
    ('ab?bc', 'abc', True),
    ('ab?bc', 'abbbbc', False),
    ('ab?c', 'abc', True),
    ('^abc$', 'abc', True),
    ('^abc$', 'abcc', False),
    ('^abc', 'abcc', True),
    ('^abc$', 'aabc', False),
    ('abc$', 'aabc', True),
    ('^', 'abc', True),
    ('$', 'abc', True),
    ('ab|cd', 'abc', True),
    ('ab|cd', 'abcd', True),
    ('()ef', 'def', True),
    ('((a))', 'abc', True),
    ('(a)b(c)', 'abc', True),
    ('a+b+c', 'aabbabc', True),
    ('(a+|b)*', 'ab', True),
    ('(a+|b)+', 'ab', True),
    ('(a+|b)?', 'ab', True),
    ('abc', '', False),
    ('a*', '', True),
    ('a|b|c|d|e', 'e', True),
    ('(a|b|c|d|e)f', 'ef', True),
    ('abcd*efg', 'abcdefg', True),
    ('ab*', 'xabyabbbz', True),
    ('ab*', 'xayabbbz', True),
    ('(ab|cd)e', 'abcde', True),
    ('^(ab|cd)e', 'abcde', False),
    ('(abc|)ef', 'abcdef', True),
    ('(a|b)c*d', 'abcd', True),
    ('(ab|ab*)bc', 'abc', True),
    ('(ab|a)b*c', 'abc', True),
    ('((a)(b)c)(d)', 'abcd', True),
    ('((((((((((a))))))))))', 'a', True),
    ('(((((((((a)))))))))', 'a', True),
    ('multiple words of text', 'uh-uh', False),
    ('multiple words', 'multiple words, yeah', True),
    (r'^((a)c)?(ab)$', 'ab', True),

]

