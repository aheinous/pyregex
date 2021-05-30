from parser import Parser
from statemachine import StateMachineBuilder
from collections import defaultdict



'''
The match tester operates on nondeterministic finte automaton (state machine)
and uses it to test whether given strings match the associated regex. Basically,
it's the part the actually tells you if regex matches a certain string.
'''


class MatchFound(Exception):
	pass


class MatchTesterFringe:

	'''
	The data structure managment component of MatchTester.
	The MatchTester runs a nondeterministic finite automaton,
	so the MatchTesterFringe contains all the states the we're in
	at the same time.
	'''

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
				self._processUnconditionals()

				self._consumeChar(c)
			self._fringe.addState(self._enter)
			self._processUnconditionals()

			self._consumeNonprinting('$')
			self._processUnconditionals()
		except MatchFound:
			return True
		return False

	def _consumeNonprinting(self, npc):
		nonprinting = self._fringe.nonprinting
		self._fringe.clearNonprinting()

		if npc in nonprinting:
			for state in nonprinting[npc]:
				self._fringe.addStates(state.connections)

	def _consumeChar(self, c):
		normal = self._fringe.normal
		self._fringe.clear()

		if c in normal:
			for state in normal[c]:
				self._fringe.addStates(state.connections)

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
