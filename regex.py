#!/usr/bin/python3

import os

''' Tokenizer ------------------------------------------ '''

class Token:
	def __init__(self, value):
		self.value = value

	def isChar(self):
		return self.value.isalnum()


class Tokenizer:
	def __init__(self, regex):
		self.regex = regex
		self.pos = 0

	def next(self):
		if self.pos >= len(self.regex):
			raise EOFError()

		if self.regex[self.pos] == '\\':
			if self.pos + 1 >= len(self.regex):
				raise EOFError()
			token = Token(self.regex[self.pos:self.pos+2])
			self.pos += 2
			return token
		token = Token(self.regex[self.pos])
		self.pos += 1
		return token

	def hasNext(self):
		return self.pos < len(self.regex)


# class Iterator:
# 	def __init__(self, stream):
# 		self.stream = stream

# 	def advance(self):

# 	def peek()

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

class ASTNodeVisitor:
	def visit(self, node):
		methodName = 'visit_' + type(node).__name__
		method = getattr(self, methodName)
		return method(node)

	def visit_ConcatNode(self, node):
		raise NotImplementedError()

	def visit_AlternationNode(self, node):
		raise NotImplementedError()

	def visit_DuplicationNode(self, node):
		raise NotImplementedError()

	def visit_CharNode(self, node):
		raise NotImplementedError()


class ASTDotGen(ASTNodeVisitor):
	def __init__(self, root):
		self.root = root
		self.nodeIDs = {}
		self.idCount = 0

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

	def getNodeID(self, node):
		if node not in self.nodeIDs.keys():
			self.idCount += 1
			self.nodeIDs[node] = self.idCount
		return self.nodeIDs[node]

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

''' Parser ------------------------------------------ '''


class ParseError(Exception):
	pass


class Parser:
	def __init__(self, regex):
		tokenizer = Tokenizer(regex)
		self.tokens = []
		try:
			while True:
				self.tokens.append(tokenizer.next())
		except EOFError:
			pass


	def parse(self):
		pos, ast = self.parse_regex(0)
		if pos != len(self.tokens):
			raise ParseError('pos={} excepted: {}'.format(pos, len(self.tokens)))
		return ast


	def parse_regex(self, pos):
		''' regex:  concatExprn '''
		return self.parse_concatExprn(pos)

	def parse_concatExprn(self, pos):
		''' concatExprn: alternationExprn + '''
		pos, altExprn = self.parse_alternationExprn(pos)
		children = [altExprn]
		try:
			while pos < len(self.tokens):
				pos, altExprn = self.parse_alternationExprn(pos)
				children.append(altExprn)
		except ParseError:
			print('caught, pos: ', pos)
			pass
		if len(children) == 1:
			return pos, children[0]
		return pos, ConcatNode(children)

	def parse_alternationExprn(self, pos):
		''' alternationExprn: duplicationExprn ('|' duplicationExprn)* '''
		pos, left = self.parse_duplicationExprn(pos)

		while pos < len(self.tokens) and self.tokens[pos].value == '|':
			pos += 1
			pos, right = self.parse_duplicationExprn(pos)
			left = AlternationNode(left, right)

		return pos, left

	def parse_duplicationExprn(self, pos):
		''' duplicationExprn: groupExprn ('*'|'+'|'?')? '''
		pos, grpExprn = self.parse_groupExprn(pos)
		if pos < len(self.tokens) and self.tokens[pos].value in ('*', '+', '?'):
			op = self.tokens[pos]
			pos += 1
			return pos, DuplicationNode(op, grpExprn)
		return pos, grpExprn

	def parse_groupExprn(self, pos):
		''' groupExprn: CHAR | '(' regex ')' '''
		if self.tokens[pos].isChar():
			return pos+1, CharNode(self.tokens[pos])
		if self.tokens[pos].value == '(':
			pos += 1
			pos, subRegex = self.parse_regex(pos)
			if self.tokens[pos].value != ')':
				print('rasing 1')
				raise ParseError()
			return pos+1, subRegex
		print('rasing 2 pos:', pos)
		raise ParseError()





def genASTTestGraphs():
	outputDir = 'ASTGraphs'
	os.system('mkdir -p ' + outputDir)
	os.system('rm  ' + outputDir + os.sep + '*')
	testCases = ['a', 'abc', 'a+', 'a*', 'a?', '(abc)+123', 'a|b|c', 'a+b*c?edf|g|(12(3(xy(123)+z)))*']
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

def main():
	genASTTestGraphs()


if __name__ == '__main__':
	main()