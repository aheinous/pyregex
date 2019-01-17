from parser import Parser
from statemachine import StateMachineBuilder

class MatchFound(Exception):
	pass

class MatchTester:
	def __init__(self, regex):
		ast = Parser(regex).parse()
		self._enter, self._exit = StateMachineBuilder(ast).genStateMachine()
		self._clear()

	def _clear(self):
		self._curUnconditionals = set()
		self._curNonprinting = set()
		self._curNormal = set()


	def _addState(self, state):
		if state is self._exit:
			raise MatchFound()
		if state.isUnconditional():
			self._curUnconditionals.add(state)
		elif state.isNonPrinting:
			self._curNonprinting.add(state)
		else:
			self._curNormal.add(state)

	def _addStates(self, states):
		for s in states:
			self._addState(s)

	def _hasState(self, state):
		return state in self._curNormal or state in self._curUnconditionals or state in self._curUnconditionals

	def matches(self, testStr):
		try:
			self._reset()
			self._consumeNonprinting('^')
			for c in testStr:
				self._addState(self._enter)
				self._consumeChar(c)
			self._consumeNonprinting('$')
		except MatchFound:
			return True
		return False

	def _consumeNonprinting(self, npc):
		nonprinting = self._curNonprinting
		self._curNonprinting = set()

		for state in nonprinting:
			if state.condition == npc:
				self._addStates(state.connections)
		self._processUnconditionals()

	def _consumeChar(self, c):
		curNormal = self._curNormal
		self._clear()

		for state in curNormal:
			if state.condition == c:
				self._addStates(state.connections)
		self._processUnconditionals()


	def _reset(self):
		self._addState(self._enter)
		self._processUnconditionals()


	def _processUnconditionals(self):
		toProcess = list(self._curUnconditionals)
		while len(toProcess) > 0:
			cur = toProcess.pop()
			if cur.isUnconditional():
				for adjacent in cur.connections:
					self._addState(adjacent)
					toProcess.append(adjacent)


