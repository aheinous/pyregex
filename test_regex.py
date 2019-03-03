import unittest
from matchtester import MatchTester


class MatcherTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass


	def testMatches(self):
		subcases = [
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
			('a*$', 'ab', False),
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
			# ('', '', True),
			('^(abc)?$', 'z', False),
			('\\+', '+', True),
			('\\+', 'a', False),
			('\\?', '?', True),
			('\\*', '*', True),
			('\\+\\+', '++', True),
			('\\+\\?\\*', '+?*', True),
			('^((a*)*)$', 'a', True),
			('^((a*)*)$', 'b', False),
			# ('a?'*100 + 'a'*100, 'a'*100 + 'b', False),



			('^abc','abcd', True),
			('^bcd','abcd', False),
			('^bcd$','bcd', True),
			('^bcd$','bcde', False),
			('','sdgsa', True),
			('','', True),
			('^$','', True),
			('^$','a', False),
		]

		for regex, canidate, expectedRes in subcases:
			with self.subTest():
				matcher = MatchTester(regex)
				res = matcher.matches(canidate)
				self.assertEqual(res, expectedRes, '\n\tregex:    {}\n\tcanidate: {}\n\texpected: {},\n\tactual:   {}'.format(regex, canidate, expectedRes, res))
