import odbc, DBcon, re, os, NCOA
from datetime import date

coa = re.compile(r'.coa$',re.IGNORECASE)
curdir = str(os.getcwd())
cdfiles = os.listdir(curdir)

#file = open('UA23201.coa','r')
# today = date.today().strftime('%Y-%m-%d')

cont = 0
dmList = ['DM1','DM3','DM6']

while cont == 0:
	company = raw_input('Enter Company: ')
	if company in dmList:
		cont = 1
	else:
		continue
		
today = raw_input('Please Enter a Date: ')

		
for i in cdfiles:
	if coa.search(i):
		file = open(i,'r')
		print 'NEW FILE:', i
		
		for line in file:
			row = NCOA.NCOA(line, company, today)
			print
			print row.dbtrID
			row.findCodes()
			row.updatePhone()
			row.updateAddress()
			row.mailReturnUpdate()
			row.updateNotes()
			
			
			
	
	
	
	
	
	
	
raw_input('dun')