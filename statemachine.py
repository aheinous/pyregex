import os

from abstract_syntax_tree import ASTNodeVisitor
from visitor import Visitor

''' State Machine ----------------------------------------- '''

class State:
	def __init__(self, condition=None, isNonPrinting=False):
		self.condition = condition
		self.connections = []
		self.isNonPrinting = isNonPrinting

	def connect(self, other):
		self.connections.append(other)

	def isUnconditional(self):
		return self.condition == None

	def __str__(self):
		return self._toString(nestLimit=4)

	def _toString(self, nestLimit=None, seen=None):
		if seen is None:
			seen = set()
		if self in seen:
			return '(***)'
		seen.add(self)
		nextNestLimit = nestLimit - 1 if nestLimit is not None else None
		selfPart = str(self.condition)

		if len(self.connections) == 0:
			otherPart = ''
		elif nestLimit == 0:
			otherPart = '...'
		else:
			otherPart = ','.join(map(lambda other: other._toString(nextNestLimit, seen), self.connections))

		return '({} {})'.format(selfPart, otherPart)


class StateGraphOptimizer:

	def __init__(self, enter, exit):
		self.enter = enter
		self.exit = exit

	def optimize(self):
		fringe = [self.enter]
		seen = set()
		while len(fringe) > 0:
			cur = fringe.pop()
			if cur in seen:
				continue
			seen.add(cur)
			self._optimizeVertex(cur)
			fringe += cur.connections
		return self.enter, self.exit

	def _optimizeVertex(self, vertex):
		toProcess = vertex.connections[:]
		newConnections = []
		seen = set()
		while len(toProcess) > 0:
			cur = toProcess.pop()
			if cur in seen:
				continue
			seen.add(cur)
			if cur.isUnconditional() and cur is not self.exit:
				toProcess += cur.connections
			else:
				newConnections.append(cur)
		vertex.connections = newConnections




class StateMachineBuilder(ASTNodeVisitor):

	def __init__(self, ast):
		self.ast = ast

	def genStateMachine(self):
		enter, exit = self.visit(self.ast)
		newExit = State()
		exit.connect(newExit)
		exit = newExit

		enter, exit = StateGraphOptimizer(enter, exit).optimize()
		return enter, exit


	def visit_ConcatNode(self, node):

		if len(node.children) == 0:
			s = State()
			return s, s

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


	def visit_AnchorNode(self, node):
		enter, exit = self.visit(node.child)

		if node.start:
			oldEnter = enter
			enter = State('^', isNonPrinting=True)
			enter.connections.append(oldEnter)

		if node.end:
			oldExit = exit
			exit = State('$', isNonPrinting=True)
			oldExit.connections.append(exit)

		return enter, exit


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

		label = 'NP ' if node.isNonPrinting else ''
		label += 'exit' if node is self.exit else node.condition if node.condition else ''

		s = '\tnode{} [label="{}"]\n'.format(
				self.getNodeID(node),
				label
			)
		for adjacent in node.connections:
			s += self.visit(adjacent)
			s += '\tnode{} -> node{} [label = "{}"]\n'.format(
					self.getNodeID(node),
					self.getNodeID(adjacent),
					''
				)
		return s



def writeStateMachineDotGraph(rootLabel, enter, exit, basename):
		dotCode = StateMachineDotGen(enter, exit).genDot(rootLabel)
		dotfname = basename + '.dot'
		pngfname = basename + '.png'
		with open(dotfname, 'w') as f:
			f.write(dotCode)

		os.system('dot -Tpng -o {png} {dot}'.format(
					png = pngfname,
					dot = dotfname
		))
