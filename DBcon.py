import odbc

def Get(db,query):
		
	con = odbc.odbc('%s/DM/******' % db)
	cur = con.cursor()
	cur.execute(query)
	dbRes = cur.fetchall()
	return dbRes
	
def Send(db,query):
		
	# try:
	con = odbc.odbc('%s/DM/******' % db)
	cur = con.cursor()
	cur.execute(query)
	# except:
		# print 'Error Occured'
	