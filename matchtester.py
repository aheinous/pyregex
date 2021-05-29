from parser import Parser
from statemachine import StateMachineBuilder
from collections import defaultdict

class MatchFound(Exception):
	pass


class MatchTesterFringe:
	def __init__(self,  exit):
		self._exit = exit
		self.clear()

	def clear(self):
		self._unconditionals = set()
		self._nonprinting = defaultdict(set)
		self._normal = defaultdict(set)

	def clearNonprinting(self):
		self._nonprinting = defaultdict(set)


	@property
	def unconditionals(self):
		return self._unconditionals

	@property
	def nonprinting(self):
		return self._nonprinting

	@property
	def normal(self):
		return self._normal


	def addState(self, state):
		if state is self._exit:
			raise MatchFound()
		if state.isUnconditional():
			self._unconditionals.add(state)
		elif state.isNonPrinting:
			self._nonprinting[state.condition].add(state)
		else:
			self._normal[state.condition].add(state)

	def addStates(self, states):
		for s in states:
			self.addState(s)

	def hasState(self, state):
		return (state.condition in self._normal
				or state.condition in self._unconditionals
				or state in self._unconditionals)

class MatchTester:
	def __init__(self, regex):
		ast = Parser(regex).parse()
		self._enter, self._exit = StateMachineBuilder(ast).genStateMachine()
		self._fringe = MatchTesterFringe(self._exit)


	def matches(self, testStr):
		try:
			self._reset()
			self._consumeNonprinting('^')
			for c in testStr:
				self._fringe.addState(self._enter)
				self._consumeChar(c)
			self._consumeNonprinting('$')
		except MatchFound:
			return True
		return False

	def _consumeNonprinting(self, npc):
		nonprinting = self._fringe.nonprinting
		self._fringe.clearNonprinting()

		if npc in nonprinting:
			for state in nonprinting[npc]:
				self._fringe.addStates(state.connections)
		self._processUnconditionals()


	def _consumeChar(self, c):
		normal = self._fringe.normal
		self._fringe.clear()

		if c in normal:
			for state in normal[c]:
				self._fringe.addStates(state.connections)

		self._processUnconditionals()


	def _reset(self):
		self._fringe.clear()
		self._fringe.addState(self._enter)
		self._processUnconditionals()


	def _processUnconditionals(self):
		toProcess = list(self._fringe.unconditionals)
		while len(toProcess) > 0:
			cur = toProcess.pop()
			for adjacent in cur.connections:
				self._fringe.addState(adjacent)

				if adjacent.isUnconditional():
					toProcess.append(adjacent)
