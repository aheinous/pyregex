from tokenizer import Tokenizer
from abstract_syntax_tree import ASTNode, ConcatNode, AlternationNode, DuplicationNode, CharNode, AnchorNode

class ParseError(Exception):
	pass


class Parser:

	'''
	Parses a regular expression into an abstract syntax tree.
	'''



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
		children = []
		try:
			while not self.tokenizer.atEnd():
				dupExprn = self.parse_duplicationExprn()
				children.append(dupExprn)
		except ParseError:
			pass
		if len(children) == 1:
			return children[0]
		return ConcatNode(children)



	def parse_anchorExprn(self):
		''' anchorExprn: '^'? concatExprn? '$'? '''

		anchorStart, anchorEnd = False, False

		if not self.tokenizer.atEnd() and self.tokenizer.cur().isSpecial() and self.tokenizer.cur().value == '^':
			anchorStart = True
			self.tokenizer.advance()

		try:
			concatNode = self.parse_concatExprn()
		except ParseError:
			concatNode = None

		if not self.tokenizer.atEnd() and self.tokenizer.cur().isSpecial() and self.tokenizer.cur().value == '$':
			anchorEnd = True
			self.tokenizer.advance()

		if not anchorStart and not anchorEnd and concatNode is None:
			raise ParseError()

		if not anchorStart and not anchorEnd:
			return concatNode

		return AnchorNode(anchorStart, anchorEnd, concatNode)



	def parse_alternationExprn(self):
		''' alternationExprn: anchorExprn ('|' anchorExprn)* '''
		left = self.parse_anchorExprn()

		while not self.tokenizer.atEnd() and self.tokenizer.cur().isSpecial() and self.tokenizer.cur().value == '|':
			self.tokenizer.advance()
			right = self.parse_anchorExprn()
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
