#!/usr/bin/python3

import os

''' Tokenizer ------------------------------------------ '''

CHAR = 'CHAR'
SPECIAL = 'SPECIAL'

class Token:
	def __init__(self, type_, value):
		self.type = type_
		self.value = value
		# print(str(self))

	def isChar(self):
		# return self.value not in ('+', '?', '*', '(' ,')')
		return self.type == CHAR

	def isSpecial(self):
		return self.type == SPECIAL

	def __str__(self):
		return 'Token({}, {})'.format(self.type, self.value)


SPECIALS = {'+','?', '*', '(', ')', '|'}
ESCAPED_SPECIALS = set(map(lambda c: '\\'+c, SPECIALS))


def tokenizeRegex(regex):
	tokens = []
	pos = 0
	while pos < len(regex):
		if regex[pos] == '\\':
			if pos+1 >= len(regex):
				raise EOFError()
			value = regex[pos: pos+2]
			pos += 2
		else:
			value = regex[pos]
			pos += 1

		if value in SPECIALS:
			tokens.append(Token(SPECIAL, value))
		elif value in ESCAPED_SPECIALS:
			tokens.append(Token(CHAR, value[1]))
		elif len(value) == 1:
			tokens.append(Token(CHAR, value))
		else:
			raise Exception('Unhandled Token: "' + value + '"')

	return tokens

class Tokenizer:
	def __init__(self, regex):
		self._tokens = tokenizeRegex(regex)
		self._pos = 0

	def cur(self):
		return self._tokens[self._pos]

	def advance(self):
		self._pos += 1
		return self._tokens[self._pos - 1]

	def atEnd(self):
		return self._pos >= len(self._tokens)

	def __str__(self):
		s = 'Tokenizer(pos={}/{}, [{}])'.format(
			self._pos,
			len(self._tokens),
			','.join(map(str, self._tokens)))
		return s



''' AST ------------------------------------------ '''

class ASTNode:
	pass

class ConcatNode(ASTNode):
	def __init__(self, children):
		self.children = children

class AlternationNode(ASTNode):
	def __init__(self, left, right):
		self.left = left
		self.right = right

class DuplicationNode(ASTNode):
	def __init__(self, op, child):
		self.op = op
		self.child = child

class CharNode(ASTNode):
	def __init__(self, char):
		self.char = char

''' AST Visitor -------------------------------- '''

class Visitor:

	def __init__(self):
		self.nodeIDs = {}
		self.idCount = 0

	def getNodeID(self, node):
		if node not in self.nodeIDs.keys():
			self.idCount += 1
			self.nodeIDs[node] = self.idCount
		return self.nodeIDs[node]

	def visit(self, node):
		methodName = 'visit_' + type(node).__name__
		method = getattr(self, methodName)
		return method(node)

class ASTNodeVisitor(Visitor):

	def __init__(self):
		super().__init__()

	def visit_ConcatNode(self, node):
		raise NotImplementedError()

	def visit_AlternationNode(self, node):
		raise NotImplementedError()

	def visit_DuplicationNode(self, node):
		raise NotImplementedError()

	def visit_CharNode(self, node):
		raise NotImplementedError()

''' AST Dot Gen Visitor -------------------------- '''






class ASTDotGen(ASTNodeVisitor):
	def __init__(self, root):
		super().__init__()
		self.root = root

	def genDot(self, rootText=None):
		s ='''
digraph astgraph {
	node [shape=circle, fontsize=12, fontname="Courier", height=.1];
	ranksep=.3;
	edge [arrowsize=.5]
'''
		if rootText is not None:
			s += '\trootText [label="{}"]\n'.format(rootText)
			s += '\trootText -> node{}\n'.format( self.getNodeID(self.root) )

		s += self.visit( self.root )
		return s +'}\n'

	def visit_ConcatNode(self, node):
		s = '\tnode{} [label="cat"]\n'.format(self.getNodeID(node))
		for child in node.children:
			s += self.visit(child)
			s += '\tnode{} -> node{}\n'.format(self.getNodeID(node), self.getNodeID(child))
		return s

	def visit_AlternationNode(self, node):
		s = '\tnode{} [label="{}"]\n'.format(self.getNodeID(node) , '|')
		s += self.visit(node.left)
		s += '\tnode{} -> node{}\n'.format(self.getNodeID(node), self.getNodeID(node.left))
		s += self.visit(node.right)
		s += '\tnode{} -> node{}\n'.format(self.getNodeID(node), self.getNodeID(node.right))
		return s

	def visit_DuplicationNode(self, node):
		s = '\tnode{} [label="{}"]\n'.format(self.getNodeID(node), node.op.value)
		s += self.visit(node.child)
		s += '\tnode{} -> node{}\n'.format(self.getNodeID(node), self.getNodeID(node.child))
		return s

	def visit_CharNode(self, node):
		s = '\tnode{} [label="{}"]\n'.format(self.getNodeID(node), node.char.value)
		return s

''' State Machine ----------------------------------------- '''

class State:
	def __init__(self, condition=None):
		self.condition = condition
		self.connections = []

	def connect(self, other):
		self.connections.append(other)

class StateMachineBuilder(ASTNodeVisitor):

	def __init__(self, ast):
		self.ast = ast

	def genStateMachine(self):
		enter, exit = self.visit(self.ast)
		newExit = State()
		exit.connect(newExit)
		return enter, newExit



	def visit_ConcatNode(self, node):
		enter, exit = self.visit(node.children[0])
		for child in node.children[1:]:
			childEnter, childExit = self.visit(child)
			exit.connect(childEnter)
			exit = childExit
		return enter, exit


	def visit_AlternationNode(self, node):
		sub0_enter, sub0_exit = self.visit(node.left)
		sub1_enter, sub1_exit = self.visit(node.right)

		enter, exit = State(), State()
		enter.connect(sub0_enter)
		enter.connect(sub1_enter)

		sub0_exit.connect(exit)
		sub1_exit.connect(exit)

		return enter, exit



	def visit_DuplicationNode(self, node):
		childEnter, childExit = self.visit(node.child)
		op = node.op.value
		if op == '?':
			enter, exit = State(), State()
			enter.connect(childEnter)
			enter.connect(exit)
			childExit.connect(exit)
			return enter, exit
		elif op == '+':
			exit = State()
			exit.connect(childEnter)
			childExit.connect(exit)
			return childEnter, exit
		elif op == '*':
			enterExit = State()
			enterExit.connect(childEnter)
			childExit.connect(enterExit)
			return enterExit, enterExit
		assert False



	def visit_CharNode(self, node):
		s = State(node.char.value)
		return s, s

''' State Machine Dot Gen --------------------------- '''


class StateMachineDotGen(Visitor):
	def __init__(self, enter, exit):
		super().__init__()
		self.enter = enter
		self.exit = exit

		self.seen = set()

	def genDot(self, rootText=None):
		s ='''
digraph astgraph {
	node [shape=circle, fontsize=12, fontname="Courier", height=.1];
	ranksep=.3;
	rankdir="LR";
	edge [arrowsize=.5]
'''
		if rootText is not None:
			s += '\trootText [label="{}"]\n'.format(rootText)
			s += '\trootText -> node{}\n'.format( self.getNodeID(self.enter) )

		s += self.visit( self.enter )
		return s +'}\n'

	def visit_State(self, node):
		if node in self.seen:
			return ''
		self.seen.add(node)

		s = '\tnode{} [label="{}"]\n'.format(
				self.getNodeID(node),
				'exit' if node is self.exit else ''
			)
		for adjacent in node.connections:
			s += self.visit(adjacent)
			s += '\tnode{} -> node{} [label = "{}"]\n'.format(
					self.getNodeID(node),
					self.getNodeID(adjacent),
					node.condition if node.condition is not None else ''
				)
		return s


''' Parser ------------------------------------------ '''


class ParseError(Exception):
	pass


class Parser:

	'''
	The order of precedence for of operators is as follows:

	Collation-related bracket symbols [==] [::] [..]
	Escaped characters \
	Character set (bracket expression) []
	Grouping ()
	Single-character-ERE duplication * + ? {m,n}
	Concatenation
	Anchoring ^$
	Alternation |
	'''

	def __init__(self, regex):
		if len(regex) == 0:
			raise Exception('zero length regex')
		self.tokenizer = Tokenizer(regex)


	def parse(self):
		ast = self.parse_regex()
		if not self.tokenizer.atEnd():
			print (self.tokenizer)
			raise ParseError()
		return ast


	def parse_regex(self):
		''' regex:  alternationExprn '''
		return self.parse_alternationExprn()




	def parse_concatExprn(self):
		''' concatExprn: duplicationExprn + '''
		dupExprn = self.parse_duplicationExprn()
		children = [dupExprn]
		try:
			while not self.tokenizer.atEnd():
				dupExprn = self.parse_duplicationExprn()
				children.append(dupExprn)
		except ParseError:
			pass
		if len(children) == 1:
			return children[0]
		return ConcatNode(children)

	def parse_alternationExprn(self):
		''' alternationExprn: concatExprn ('|' concatExprn)* '''
		left = self.parse_concatExprn()

		while not self.tokenizer.atEnd() and self.tokenizer.cur().isSpecial() and self.tokenizer.cur().value == '|':
			self.tokenizer.advance()
			right = self.parse_concatExprn()
			left = AlternationNode(left, right)

		return left

	def parse_duplicationExprn(self):
		''' duplicationExprn: groupExprn ('*'|'+'|'?')? '''
		grpExprn = self.parse_groupExprn()

		if not self.tokenizer.atEnd() and self.tokenizer.cur().isSpecial() and self.tokenizer.cur().value in ('*', '+', '?'):
			op = self.tokenizer.advance()
			return DuplicationNode(op, grpExprn)
		return grpExprn

	def parse_groupExprn(self):
		''' groupExprn: CHAR | '(' regex ')' '''
		if self.tokenizer.cur().isChar():
			return CharNode(self.tokenizer.advance())
		if self.tokenizer.cur().value == '(':
			self.tokenizer.advance()
			subRegex = self.parse_regex()
			if self.tokenizer.cur().value != ')':
				raise ParseError()
			self.tokenizer.advance()
			return  subRegex
		raise ParseError()


''' Regex Test ------------------------------------- '''

class RegexMatcher:
	def __init__(self, regex):
		ast = Parser(regex).parse()
		self.enter, self.exit = StateMachineBuilder(ast).genStateMachine()
		self.curStates = set()

	def matches(self, testStr):
		# print('len states: ', len(self.curStates))
		self.reset()
		# print('len states: ', len(self.curStates))
		for c in testStr:
			# print('consume: ', c)
			self.consumeChar(c)
			# print('len states: ', len(self.curStates))
		return self.exit in self.curStates

	def consumeChar(self, c):
		nextStates = set()
		for state in self.curStates:
			# print('>>', state.condition, c)
			if state.condition == c:
				nextStates.add(*state.connections)
		self.curStates = nextStates
		self.addUnconditionals()


	def reset(self):
		self.curStates = { self.enter }
		self.addUnconditionals()


	def addUnconditionals(self):
		toProcess = list(self.curStates)
		while len(toProcess) > 0:
			cur = toProcess.pop()
			if cur.condition is None:
				for adjacent in cur.connections:
					if adjacent not in self.curStates:
						self.curStates.add(adjacent)
						toProcess.append(adjacent)



''' main and friends ------------------------------- '''


testCases = ['a', 'abc','(abc)*', 'a+', 'a*', 'a?', '(abc)+123', 'a|b123|c', 'a+b*c?edf|g|(12(3(xy(123)+z)))*', '\\+\\?\\*']

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
		('abcd', 'abcd', True),
		('abcd', 'abc', False),
		('abc', 'abcd', False),
		('abcd', 'bcd', False),
		('bcd', 'abcd', False),
		('a*', 'a', True),
		('a*', 'aaaa', True),
		('a*', '', True),
		('a*', 'b', False),
		('a*', 'ab', False),
		('a*b', 'aaaab', True),
		('a|b|c', 'a', True),
		('a|b|c', 'b', True),
		('a|b|c', 'c', True),
		('a|b|c', 'd', False),
		('a|b|c', 'ab', False),
		('(abc)+', 'abc', True),
		('(abc)+', 'abcabc', True),
		('(abc)+', 'abcabcabc', True),
		('(abc)+', 'abcabcab', False),
		('(abc)+', 'abcabcaba', False),
		('(abc)+', '', False),
		('(abc)*', '', True),
		('(abc)?', '', True),
		('(abc)?', 'abc', True),
		# ('', '', True),
		('(abc)?', 'z', False),
		('\\+', '+', True),
		('\\+', 'a', False),
		('\\?', '?', True),
		('\\*', '*', True),
		('\\+\\+', '++', True),
		('\\+\\?\\*', '+?*', True),
		# ('a?'*100 + 'a'*100, 'a'*100 , True),
		('a?'*100 + 'a'*100, 'a'*100 + 'b', False),
		('a?'*1000 + 'a'*1000, 'a'*1000 + 'b', False),
		# ('a?'*10000 + 'a'*10000, 'a'*10000 + 'b', False),
		# ('a?'*100000 + 'a'*100000, 'a'*100000 + 'b', False),
	]

	passed = 0
	for regex, canidate, expectedRes in testCases:
		print('--------------------------------------------------------')
		matcher = RegexMatcher(regex)
		res = matcher.matches(canidate)
		print('SUCCESS' if expectedRes == res else 'FAILURE')
		print('\t{}\n\t{}\n\texpected: {}\n\tactual:   {}'.format(regex, canidate, expectedRes, res))
		passed += (expectedRes == res)
		print('--------------------------------------------------------')
		# return
	print('PASSED: {} / {}'.format(passed, len(testCases)))


def main():
	genASTTestGraphs()
	genTestStateMachines()
	matchTests()


if __name__ == '__main__':
	main()
