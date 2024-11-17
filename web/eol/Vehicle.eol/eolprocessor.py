from labdash.eolclass import EOLClass



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
		self.load_procedures()
		self.displayWrite("Moin")
		data= [
			{
				"id":"4711",
				"parent":None,
				"text":"Inbetriebnahme"
			},
			{
				"id":"4712",
				"parent":"4711",
				"text":"Motor"
			},
			{
				"id":"4713",
				"parent":"4712",
				"text":"Kühlwasser"
			},
			{
				"id":"4714",
				"parent":"4711",
				"text":"Kabine"
			},
			{
				"id":"4715",
				"parent":"4714",
				"text":"Display"
			}
		]
		self.eollist("ich bin der Titel",data)
		return oldvalue