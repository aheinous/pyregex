import os

from visitor import Visitor


''' Nodes ------------------------------------------ '''

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

class AnchorNode(ASTNode):
	def __init__(self, start, end, child):
		self.start = start
		self.end = end
		self.child = child

''' AST Visitor -------------------------------- '''



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

	def visit_AnchorNode(self, node):
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



	def visit_AnchorNode(self, node):
		label = '{} anchor {}'.format(
			'^' if node.start else '',
			'$' if node.end else ''
		)
		s = '\tnode{} [label="{}"]\n'.format(self.getNodeID(node), label)
		s += self.visit(node.child)
		s += '\tnode{} -> node{}\n'.format(self.getNodeID(node), self.getNodeID(node.child))
		return s


def writeASTDotGraph(rootLabel, ast, basename):
		dotCode = ASTDotGen(ast).genDot(rootLabel)
		dotfname = basename + '.dot'
		pngfname = basename + '.png'
		with open(dotfname, 'w') as f:
			f.write(dotCode)

		os.system('dot -Tpng -o {png} {dot}'.format(
					png = pngfname,
					dot = dotfname
		))
