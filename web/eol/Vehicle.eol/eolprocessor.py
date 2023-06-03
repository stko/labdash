from eolclass import EOLClass



class EOL(EOLClass):

	myedit=""

	def showlastValue(self,oldvalue,id):
		return self.myedit

	def bool(self,oldvalue,id):
		self.myedit =oldvalue
		return self.myedit

	def edittext(self,oldvalue,id):
		self.myedit =oldvalue
		return self.myedit

	def donothing(self,oldvalue,id):
		self.myedit =oldvalue
		return self.myedit

	def donothing2(self,oldvalue,id):
		self.myedit =oldvalue
		return self.myedit

	def main(self,oldvalue,id):
		print('tärä!')
		self.displayWrite("Moin")
		data= [
			{
				"id":"4711",
				"parent":None,
				"text":"master"
			},
			{
				"id":"4712",
				"parent":"4711",
				"text":"bla"
			}
		]
		self.eollist("ich bin der Titel",data)
		return oldvalue