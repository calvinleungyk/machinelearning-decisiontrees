import re
import math
from queue import Queue
import copy
class DecisionTree:
	"""
	A class that constructs a decision tree and provides helper functions to print and use the tree.
	"""

	def __init__(self, name, attributes, datalines):
		self.name = name
		self.attributes = attributes
		self.root = None
		self.datalines = datalines
		self.size = 0

	def computeParentGain(self, datalines):
		yes = 0
		no = 0
		for dataline in datalines:
			if dataline[-1] == 'Yes':
				yes = yes + 1
			else:
				no = no + 1
		yes_prob = yes/len(datalines)
		no_prob = no/len(datalines)
		result = 0
		if (yes_prob != 0):
			result += (- (yes_prob) * math.log(yes_prob, 2))
		if (no_prob != 0):
			 result += (- (no_prob) * math.log(no_prob, 2))
		return result

	def computeAvgChildGain(self, datalines, attribute_num, attributes, splitted_data):
		attribute_name = attributes[attribute_num][0]
		probabilities = []
		for i in range(1, len(attributes[attribute_num])):
			probabilities.append(0)
			attribute_value = attributes[attribute_num][i]
			for dataline in datalines:
				if dataline[attribute_num] == attribute_value:
					probabilities[i-1] += 1 
		avg_child_gain = 0
		for i in range(0, len(probabilities)):
			probabilities[i] = probabilities[i] / len(datalines)
			if probabilities[i] != 0:
				avg_child_gain += ((probabilities[i]) * self.computeParentGain(splitted_data[i]) )
		return avg_child_gain

	def maxInformationGain(self, datalines, attributes, curr_node):
		data_size = len(datalines)
		max_gain = 0
		max_gain_attribute = -1
		parent_gain = self.computeParentGain(datalines)
		for i in range(0, len(attributes)):
			if curr_node and i in curr_node.attribute_history:
				continue
			splitted_data = self.splitData(attributes[i], datalines, i)
			avg_child_gain = self.computeAvgChildGain(datalines, i, attributes, splitted_data[2])
			total_gain = 0
			if self.size <= 1:
				total_gain = parent_gain - avg_child_gain
			else:
				total_gain = parent_gain - avg_child_gain
			if total_gain > max_gain:
				max_gain = total_gain
				max_gain_attribute = i
		return max_gain_attribute

	# splits data 
	def splitData(self, attribute_array, datalines, attribute_num):
		splitted_data = []
		for i in range (0, len(attribute_array)-1):
			splitted_data.append([])

		attribute_name = attribute_array[0]
		attribute_values = attribute_array[1:]

		for dataline in datalines:
			for i in range (0, len(attribute_values)):
				if dataline[attribute_num] == attribute_values[i]:
					splitted_data[i].append(dataline)
		return_array = []
		return_array.append(attribute_name)
		return_array.append(attribute_values)
		return_array.append(splitted_data)
		return return_array

	# TODO: add list of unused attributes numbers to node
	def addTreeNode(self, name, edge_names, curr_data, curr_node):
		# add attribte numbers
		new_node = None
		if self.root == None:
			self.root = TreeNode(name, edge_names, curr_data, curr_node)
		else:
			new_node = TreeNode(name, edge_names, curr_data, curr_node)
			new_node.parent = curr_node
			curr_node.children.append(new_node)
		self.size += 1
		return new_node

	def printTree(self):
		curr_lv = [self.root]
		while curr_lv:
			next_lv = []
			for node in curr_lv:
				print (node.name, " ", end = "")
				if not node.isLeaf:
					for child in node.children:
						next_lv.append(child)
			print ()
			curr_lv = next_lv

	def isPureClass(self, datalines):
		label = datalines[0][-1]
		for dataline in datalines:
			if dataline[-1] != label:
				return False
		return True

	def assignLabel(self, datalines, curr_node):
		yes = 0
		no = 0
		for dataline in datalines:
			if dataline[-1] == 'Yes':
				yes += 1
			else:
				no += 1
		if yes > no:
			return 'Yes'
		elif no > yes:
			return 'No'
		else:
			return self.assignLabel(curr_node.parent.curr_data, curr_node.parent)

	def id3(self, datalines, attributes):
		init_max_gain = self.maxInformationGain(datalines, attributes, None)
		init_split = self.splitData(attributes[init_max_gain], datalines, init_max_gain)
		self.addTreeNode(attributes[init_max_gain][0], attributes[init_max_gain][1:], datalines, None)
		queue = Queue()
		queue.put(self.root)
		while queue.empty() != True:
			curr_node = queue.get()
			if len(curr_node.curr_data) == 0:
				curr_node.name = self.assignLabel(curr_node.curr_data, curr_node)
				curr_node.children = None
				curr_node.isLeaf = True
				curr_node.edge_names = None
				continue
			if (curr_node.attribute_history and len(curr_node.attribute_history)) == 7:
				curr_node.name = self.assignLabel(curr_node.curr_data, curr_node)
				curr_node.children = None
				curr_node.isLeaf = True
				curr_node.edge_names = None
				continue

			if self.isPureClass(curr_node.curr_data):
				curr_node.name = curr_node.curr_data[0][-1]
				curr_node.children = None
				curr_node.isLeaf = True
				curr_node.edge_names = None
				continue
			max_gain_attribute = self.maxInformationGain(curr_node.curr_data, attributes, curr_node)
			splitted_data = self.splitData(attributes[max_gain_attribute], curr_node.curr_data, max_gain_attribute)
			curr_node.name = splitted_data[0]
			curr_node.edge_names = splitted_data[1]
			curr_node.attribute_num = max_gain_attribute
			if curr_node.parent:
				for a in curr_node.parent.attribute_history:
					curr_node.attribute_history.add(a)
			curr_node.attribute_history.add(max_gain_attribute)
			# add edge_names to current node
			for i in range(0, len(splitted_data[1])):
				new_node = self.addTreeNode('from ' + curr_node.name, None, splitted_data[2][i], curr_node)
				queue.put(new_node)

		return
		# check upper decision if runs out of data

	# predict_values in format ['attribute_name', 'value']
	def predict(self, root, attributes):
		predict_values = [['Size', 'Large'], ['Occupied', 'Moderate'], ['Price', 'Cheap'], ['Music', 'Loud'], ['Location', 'City-Center'], ['VIP', 'No'], ['Favorite', 'No']]
		while root.isLeaf != True:
			predict_value = predict_values[root.attribute_num][1]
			found = False
			for i in range (0, len(root.edge_names)):
				if root.edge_names[i] == predict_value:
					root = root.children[i]
					break
		return root.name

class TreeNode:
	"""
	A class that represents a tree node in a decision tree.
	"""

	def __init__(self, name, edge_names, curr_data, parent):
		self.name = name
		self.edge_names = edge_names
		self.curr_data = []
		for i in curr_data:
			self.curr_data.append(i)
		self.children = []
		self.isLeaf = False
		self.attribute_num = None
		self.attribute_history = set()
		self.parent = parent

class Variable:
	"""
	A class that defines a variable or a feature to split dataset.  Contains possible values of variable.
	"""

	"""
	Takes a string as name and an array of 
	"""
	def __init__(self, name, values):
		self.name = name
		self.values = values


def readData():
	data = []
	with open('dt-data.txt', 'r') as rawdata:
		lines = rawdata.readlines()
		for i in range(len(lines)):
			if lines[i] != '\n':
				data.append(lines[i])
	return data

def addAttributes(data):
	attributes = []
	attribute_names = re.split('\W+', data[0])
	del attribute_names[0]
	del attribute_names[-1]
	for name in attribute_names:
		attributes.append([name])
	attributes.remove(['Favorite'])
	attributes.remove(['Enjoy'])
	return attributes

def addDatalines(data, attributes):
	dataline = []
	for i in range(1,len(data)):
		attribute_value = re.split('[^\w-]+', data[i])
		del attribute_value[0]
		del attribute_value[-1]
		for j in range(0, len(attribute_value)-1):
			if attribute_value[j] not in attributes[j]:
				attributes[j].append(attribute_value[j])
		dataline.append(attribute_value)

	return dataline

# first read rawdata from text file
data = readData()

# add to attributes
attributes = addAttributes(data)

# separate lines in text file into values in list
datalines = addDatalines(data, attributes)

decision_tree = DecisionTree("decision tree", attributes, datalines)
decision_tree.id3(datalines, attributes)
decision_tree.printTree()
print('Prediction for given data is: ', decision_tree.predict(decision_tree.root, attributes))
