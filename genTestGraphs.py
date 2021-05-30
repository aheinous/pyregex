#!/usr/bin/python3

import os

from abstract_syntax_tree import writeASTDotGraph
from statemachine import StateMachineBuilder, writeStateMachineDotGraph
from parser import Parser
from matchtester import MatchTester




''' main and friends ------------------------------- '''


graphTestCases = ['a',
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
	basename = outputDir + os.sep + 'ast'
	for n, regex in enumerate(graphTestCases):
		ast = Parser(regex).parse()
		writeASTDotGraph(regex, ast, basename+str(n))
	os.system('xdg-open {}0.png'.format(basename))



def genStateMachinesTestGraphs():
	outputDir = 'StateGraphs'
	os.system('mkdir -p ' + outputDir)
	os.system('rm  ' + outputDir + os.sep + '*')
	basename = outputDir + os.sep + 'state-machine'
	for n, regex in enumerate(graphTestCases):
		ast = Parser(regex).parse()
		enter, exit = StateMachineBuilder(ast).genStateMachine()
		writeStateMachineDotGraph(regex, enter, exit, basename+str(n))
	os.system('xdg-open {}0.png'.format(basename))



def main():
	genASTTestGraphs()
	genStateMachinesTestGraphs()




if __name__ == '__main__':
	main()
