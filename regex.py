#!/usr/bin/python3

import os

from ast import ASTDotGen
from statemachine import StateMachineBuilder, StateMachineDotGen
from parser import Parser
from matchtester import MatchTester




''' main and friends ------------------------------- '''


testCases = ['a',
 				'(a*)*',
 				'abc',
 				'(abc)*',
 				'a+',
 				'a*',
 				'a?',
 				'(abc)+123',
 				'a|b123|c',
 				'a+b*c?edf|g|(12(3(xy(123)+z)))*',
 				'\\+\\?\\*',

 				'^a',
 				'a$',
 				'^a$',
 				''
 				'^$'

 				]

def genASTTestGraphs():
	outputDir = 'ASTGraphs'
	os.system('mkdir -p ' + outputDir)
	os.system('rm  ' + outputDir + os.sep + '*')
	# testCases = ['a', 'abc', 'a+', 'a*', 'a?', '(abc)+123', 'a|b|c', 'a+b*c?edf|g|(12(3(xy(123)+z)))*']
	for n, regex in enumerate(testCases):
		print('--------------------------------------------------------')
		print(regex,'\n')
		ast = Parser(regex).parse()
		dotCode = ASTDotGen(ast).genDot(regex)
		print(dotCode)

		fname = outputDir + os.sep + 'ast{}.dot'.format(n)
		with open(fname, 'w') as f:
			f.write(dotCode)

		os.system('cd {outputDir} && dot -Tpng -o ast{n}.png ast{n}.dot'.format(
					outputDir=outputDir,
					n=n) )


		print('--------------------------------------------------------')
	os.system('cd {outputDir} && xdg-open ast0.png'.format(outputDir=outputDir))


def genTestStateMachines():

	outputDir = 'StateGraphs'
	os.system('mkdir -p ' + outputDir)
	os.system('rm  ' + outputDir + os.sep + '*')

	for n, regex in enumerate(testCases):
		print('--------------------------------------------------------')
		print(regex,'\n')
		ast = Parser(regex).parse()
		enter, exit = StateMachineBuilder(ast).genStateMachine()

		dotCode = StateMachineDotGen(enter, exit).genDot(regex)
		print(dotCode)

		fname = outputDir + os.sep + 'sm{}.dot'.format(n)
		with open(fname, 'w') as f:
			f.write(dotCode)

		os.system('cd {outputDir} && dot -Tpng -o sm{n}.png sm{n}.dot'.format(
					outputDir=outputDir,
					n=n) )


		print('--------------------------------------------------------')
	os.system('cd {outputDir} && xdg-open sm0.png'.format(outputDir=outputDir))



def matchTests():
	testCases = [
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

	passed = 0
	for regex, canidate, expectedRes in testCases:
		print('--------------------------------------------------------')
		try:
			matcher = MatchTester(regex)
			res = matcher.matches(canidate)
		except Exception as e:
			res = e
		passed += (expectedRes == res)
		print('SUCCESS' if expectedRes == res else 'FAILURE')
		print('\t{}\n\t{}\n\texpected: {}\n\tactual:   {}'.format(regex, canidate, expectedRes, res))
		print('--------------------------------------------------------')
		# return
	print('PASSED: {} / {}'.format(passed, len(testCases)))


def main():
	genASTTestGraphs()
	genTestStateMachines()
	matchTests()


if __name__ == '__main__':
	main()
