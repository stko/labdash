from labdash.ldmclass import LDMClass



class LDM(LDMClass):

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
		self.openPage("OOBD UI Test")
		self.addElement("Text Input", "edittext","Input some Text here", 0x0, "", {  'type': "TextEdit" } )
		self.addElement("Text Input with Regex (\\d\\d)", "edittext","Input some Text here", 0x0, "", {  'type':"TextEdit" , 'regex' :"\\d\\d" } )
		self.addElement("Click here to see last input value", "showlastValue", self.myedit, 0x0, "")
		self.addElement("Checkbox with longer Text...", "bool","True",0x0, "",{ 'type' : "CheckBox" } )
		self.addElement("Value Slider", "donothing","40",0x0, "",{  'type':"Slider", 'min':10, 'max':60})
		self.addElement("Gauge with last Slider Value", "donothing","40",0x0, "",{  'type':"Gauge", 'min':10, 'low':20 , 'optimum': 30, 'high':50 , 'max':60, 'unit':" km/h"} )
		self.addElement("Combobox", "donothing2","2",0x0, "",{  'type':"Combo", 'content':["one","two","three","four","five","six"]} )
		self.pageDone()
		return oldvalue