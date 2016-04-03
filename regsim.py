#! /usr/bin/python

#IMPORT STUFF
import psycopg2, time, datetime, random

#Setup DB Connection
conn = psycopg2.connect(database=db,user=dbuser,host=dbhost,password=dbpass")
cursor = conn.cursor()


### Function Definitions
#Define DB queries
def write_dirty():
	cursor.execute("INSERT INTO transactionsimulation (tsn_tstate) VALUES (1);")
	conn.commit()

def write_clean():
	cursor.execute("INSERT INTO transactionsimulation (tsn_tstate) VALUES (0);")
	conn.commit()

#Define rolldice
def rolldice(thresh):
	if random.randrange(100) <= thresh:
		write_dirty()
		return 1
	else:
		write_clean()
		return 0


#main loop
Ti = datetime.datetime.now()
dT = datetime.timedelta(0,10)
Tt = datetime.datetime.now() + datetime.timedelta(0,1200)

#initiate main loop
thresh = 25
while datetime.datetime.now() < Tt:
	#main program function
	#thresh = 25
	rolldice(thresh)
	#if a == 0:
	#	thresh += 25
	#else:
	#	thresh = 25
	T0 = datetime.datetime.now()
	while datetime.datetime.now() < T0 + dT:
		time.sleep(5)

conn.close()
