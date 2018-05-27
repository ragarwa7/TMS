"""
Author - 
Name: Rachit Agarwal
unitityId: ragarwa7

"""

import re
from collections import OrderedDict
import Queue
import sys


"""
    Class for Truth Maintainance System
    Param: File containing list of Tell and Retract statements
"""		
class TMS:
	
	"""
		global variables to store list of action from input files, maintain the current stats record, graph to store relation between literals 
		count number of states
	"""
	actions = []
	statusrecord = OrderedDict()
	li_graph = {}
	tms_list = []
	count = 1

	"""
        This fucntion is used to read input file
        Param: path
    """
	def populateTMS(self, path):
		file = open(path,"r")
		line = file.read()

		self.actions = line.split("\n")

	"""
        This fucntion is called in case of tell statement to update TMS
        Param: action
    """
	def  tellTMS(self, action):
		temp_status = self.statusrecord.copy()
		if not self.conflict(action):
			if ">" in action:
				self.statusrecord[self.count] = action
				self.count+=1
				parent = action.replace("(","").replace(")","")
				temp = action.split(">")
				self.parseImplication(temp[0], temp[1])
				if "+" in parent:
					parents = parent.split("+")
					result = self.updateTMS(parents[0], temp[1])
					result = self.updateTMS(parents[1], temp[1])
				elif "*" in parent:
					parents = parent.split("*")
					result = self.updateTMS(parents[0], temp[1])
					result = self.updateTMS(parents[1], temp[1])
				else:
					result = self.updateTMS(temp[0], temp[1])
			
			else:
				self.statusrecord[action] = action
				result = self.updateTMS(action, None)

			if not result:
				self.statusrecord = temp_status 
			
		
	"""
        This fucntion is used to parse the iput action and further update the graph
        Param: parent, child. ex: A+B>C,  here A, B are parents and C is child
    """
	def parseImplication(self, parent, child):
		parent = parent.replace("(","").replace(")","")
		parents = [parent]
		if "+" in parent:
			parents = parent.split("+")
		elif "*" in parent:
			parents = parent.split("*")

		self.updateGraph(parents, child)
		

	"""
        This fucntion is used to update the graph for the input relation
        Param: parent, child. ex: A+B>C,  here A, B are parents and C is child
    """
	def updateGraph(self, parents, child):
		for parent in parents:
			if parent in self.li_graph.keys():
				temp = self.li_graph[parent]
				if child not in temp:
					temp = temp + [child]
					self.li_graph[parent] = temp
			else:
				self.li_graph[parent] = [child]
				#print self.li_graph
	
	"""
        This fucntion uses the BFS search to update the TMS for all the literals getting impacted due to new fact
        Param: parent, child. ex: A+B>C,  here A, B are parents and C is child
    """
	def updateTMS(self, parent, child):
		action = parent
		temp_map = self.li_graph.copy()
		queue = Queue.Queue()
		if action in temp_map.keys():
			queue.put(temp_map[action])
			temp_map.pop(action, None)
			while not queue.empty():
				nodes = queue.get()
				for node in nodes:
					for key,value in self.statusrecord.iteritems():
						if not isinstance(key, basestring) and node in value and parent in value and (parent in self.statusrecord.keys() or parent + ":" in self.statusrecord.keys()):
							if "*" not in value:
								if self.conflict(node):
									return False
								justification = "{" + parent + "," + value + "}"
								#print justification
								if node + ":" in self.statusrecord.keys():
									if justification not in self.statusrecord[node + ":"]:
										self.statusrecord[node + ":"] =  self.statusrecord[node + ":"] + "," + justification
								else:
									self.statusrecord[node + ":"] = node + ":" + justification
							else:
								check_lit = value.split(">")[0].split("*")[1].replace(")","")
								if check_lit in self.statusrecord.keys() or check_lit + ":" in self.statusrecord.keys():
									if self.conflict(node):
										return False
									justification = "{" + parent + "," + value + "}"
									justification2 = "{" + check_lit + "," + value + "}"
									#print justification
									if node + ":" in self.statusrecord.keys():
										if justification not in self.statusrecord[node + ":"]:
											self.statusrecord[node + ":"] =  self.statusrecord[node + ":"] + "," + justification
									else:
										self.statusrecord[node + ":"] = node + ":" + justification + "," + justification2
							self.updateTMS(node, None)
					if node in temp_map.keys():
						queue.put(temp_map[node])
					temp_map.pop(node, None)
		return True


	"""
        This fucntion is used to check the conflicts in case of updating the TMS 
        Param: action
    """
	def conflict(self,action):
		if len(action) < 3:
			if "-" in action:
				action = action.replace("-", "")
				if action in self.statusrecord.keys() or action+":" in self.statusrecord.keys():
					print "conflict", action, "-" + action
					return True	
			elif "-"+action in self.statusrecord or "-"+action+":" in self.statusrecord.keys():
					print "conflict", action, "-"+action
					return True		
		return False

	"""
        This fucntion is called in case of retract statement to update TMS
        Param: action
    """
	def retractTMS(self, action):
		temp_map = self.li_graph.copy()
		queue = Queue.Queue()
		if action in temp_map.keys():
			queue.put(temp_map[action])
			temp_map.pop(action, None)
			if action in self.statusrecord.keys():
				self.statusrecord.pop(action, None)
			while not queue.empty():
				nodes = queue.get()
				for node in nodes:
					regex = r"\{(.*?)\}"
					state = ""
					if node in self.statusrecord.keys():
						state = self.statusrecord[node]
					elif node + ":" in self.statusrecord.keys():
						state = self.statusrecord[node+":"]
					else:
						continue
					matches = re.finditer(regex, state, re.MULTILINE | re.DOTALL)
					self.updateTMSRetract(matches, node)
					if node in temp_map.keys():
						queue.put(temp_map[node])
					temp_map.pop(node, None)


	"""
        This fucntion uses the BFS search to update the TMS for all the literals getting impacted while retracting a literal
        Param: matches, node
    """	
	def updateTMSRetract(self, matches, node):

		just_list = []
		for matchNum, match in enumerate(matches):
			for groupNum in range(0, len(match.groups())):
				just_list.append(match.group(1))
		
		for literal in just_list:
			temp = literal.split(",")[0]
			if (temp not in self.statusrecord.keys() and temp+":" not in self.statusrecord.keys()) or "*" in literal:
				if len(just_list) == 1:
					self.statusrecord.pop(node + ":", None)
				elif "+" in literal:
					justification = self.statusrecord[node+":"]
					justification = justification.replace("{"+ literal + "},", "")
					self.statusrecord[node+":"] = justification
				elif "*" in literal:
					temp1 = literal.split("*")
					if (temp1[0][-1] not in self.statusrecord.keys() and temp1[0][-1]+":" not in self.statusrecord.keys()) or (temp1[1][0] not in self.statusrecord.keys() and temp1[1][0]+":" not in self.statusrecord.keys()):
						if len(just_list) <= 2:
							self.statusrecord.pop(node + ":", None)
						else:
							if node + ":" in self.statusrecord.keys():
								justification = self.statusrecord[node+":"]
								justification = justification.replace("{"+ literal + "},", "")
								self.statusrecord[node+":"] = justification
								self.updateTMSRetract(re.finditer(r"\{(.*?)\}", self.statusrecord[node+":"], re.MULTILINE | re.DOTALL), node)
	
	
	def format(self,action):
		temp = "("
		if "+" in action:
			actions = action.split("(")[1].split("+")[0]
			temp = temp + self.formatnegate(actions)+ "*"
			actions = action.split("(")[1].split("+")[1].split(")")[0]
			temp = temp + self.formatnegate(actions) + ")>" + action.split(">")[1]
			return temp
		elif "*" in action:
			actions = action.split("(")[1].split("*")[0]
			temp = temp + self.formatnegate(actions)+ "+"
			actions = action.split("(")[1].split("*")[1].split(")")[0]
			temp = temp + self.formatnegate(actions) + ")>" + action.split(">")[1]
			return temp
		else:
			return self.formatnegate(action).replace("(","").replace(")","")


	def formatnegate(self,action):
		if "-" in action:
			return action.replace("-","")
		else:
			return "-"+ action

	def printTMS(self):
		print ""
		for key,value in self.statusrecord.iteritems():
			if value is not None:
				print value
"""
    Main method : TMS.py
    Arguments: filPath
"""  
if __name__ == "__main__":
        param = sys.argv

        if len(param) > 1:
        	tms = param[1]
        else:
        	tms = "TMS.txt"

        tms_system = TMS()
        tms_system.populateTMS(tms)

        for input in tms_system.actions: 
        	action = input.replace(" ",'').split(":")
        	if len(action) > 1:
	        	if action[0].lower() == "tell":
	        		tms_system.tellTMS(action[1])
	        	else:
	        	 	tms_system.retractTMS(action[1])

        tms_system.printTMS()
        print tms_system.format("-(-A+C)>D")