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
