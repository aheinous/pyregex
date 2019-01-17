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


SPECIALS = {'+','?', '*', '(', ')', '|', '^', '$'}
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
