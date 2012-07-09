import DBcon
from datetime import date


today = date.today().strftime('%Y-%m-%d')

class NCOA:
	
	def __init__(self, line, DM, fileDate=today):
		
		self.line = line
		self.company = DM										# Which Debtmaster
		self.niCode = line[0:26].strip()						# A=Moved, C=No Match
		self.ncCode = line[26]									# M=Moved, G=Closed Box, K=No Forward Address
		self.newAddress = line[27:75].rstrip()
		self.newCity = line[75:103].rstrip()
		self.newState = line[103:105]
		self.newZip = line[105:110]
		self.moveType = line[117]								# B=Business, I=Individual, F=Family
		self.moveDate = line[120:122] + '/' + line[118:120]		# YYMM
		self.passedAddress = line[163:211].rstrip()
		self.passedCity = line[211:239].rstrip()
		self.passedState = line[239:241]
		self.passedZip = line[241:246]
		self.phoneStatus = line[291]
		self.phone = line[273:283]
		self.dbtrID = self.line[495:540].strip().split('-')[0]
		self.daCode = 0
		self.note = []
		self.fileDate = fileDate
		
	def findCodes(self):
		if self.niCode == 'A' and self.ncCode == 'M':
			self.note.append('Dbtr Moved-Fowarding Address Found')
			self.note.append('%s' % (self.newAddress))
			self.note.append('%s, %s %s' % (self.newCity,self.newState,self.newZip))
			self.note.append('Move Effective: %s' % (self.moveDate))
		elif self.niCode == 'A' and self.ncCode == 'K':
			self.note.append('Dbtr Moved-No Fowarding Address Found')
		elif self.niCode == 'A' and self.ncCode == 'G':
			self.note.append('Dbtr Moved-No Fowarding Address Found')
		elif self.niCode == 'C' and self.ncCode == ' ':
			self.note.append('NCOA File Rcvd-No Move Found')
		elif self.niCode == 'C' and self.ncCode == 'G':
			self.note.append('NCOA File Rcvd-Bad Address')
		else:
			print 'Unrecognized Code'
			print self.niCode, self.ncCode, '\n\n'
		
		
	def phoneItem(self):
		query = "SELECT MIN(item_no) FROM DBTRPHON WHERE debtor_id = %s" % self.dbtrID
		try:
			itemPhoneNo = DBcon.Get(self.company,query)[0][0] -1
		except:
			itemPhoneNo = -1
		return itemPhoneNo
		
	
	def addressItem(self):
		itemAddrQuery = "SELECT MIN(item_no) FROM DBTRADDR WHERE debtor_id = %s" % self.dbtrID
		try:
			itemAddrNo = DBcon.Get(self.company,itemAddrQuery)[0][0] -1
		except:
			itemAddrNo = -1
		return itemAddrNo	
		
	
	def updatePhone(self):
		if self.phoneStatus == 'S':
			itemPhoneNo = self.phoneItem()
			query = "INSERT INTO DBTRPHON(debtor_id, item_no, phone, descr, status) VALUES(%s, %i, '%s', 'NCOA', 'A' )" % (self.dbtrID, itemPhoneNo, self.phone)
			DBcon.Send(self.company, query)
			self.note.append("NCOA New Phone Found")
			
	
	def updateAddress(self):
		itemAddrNo = self.addressItem()
		if self.niCode == 'A' and self.ncCode == 'M':
			query = "INSERT INTO DBTRADDR(debtor_id, item_no, addr1, city, state, zip) VALUES('%s', %i, '%s', '%s', '%s', '%s')" % (self.dbtrID, itemAddrNo, self.newAddress, self.newCity, self.newState, self.newZip)
			DBcon.Send(self.company, query)
			self.mailReturnUpdate()
			
	
	def updateNotes(self):
		if self.note:
			for eachNote in self.note:
				query = "INSERT INTO DBTRACT(debtor_id, item_no, act_date, user_id, comments, user_id_stamp,gmt_offset,act_time) VALUES(%s, NULL, '%s', 'SKP', '%s', 'ACS', 0 , '12:00:00')" % (self.dbtrID, self.fileDate, eachNote)
				DBcon.Send(self.company,query)
	
	
	def mailReturnUpdate(self):
		if self.niCode != 'C' and self.ncCode != ' ':
			query = "UPDATE DBTRADDR SET mail_rtn = 'T' WHERE debtor_id = %s and SOUNDEX(addr1) = SOUNDEX('%s')" % (self.dbtrID, self.passedAddress.upper())
			DBcon.Send(self.company, query)
		
	
	