#! /usr/bin/python

#IMPORT STUFF
import psycopg2, time, datetime, random

DATABASE = 'database'
USER     = 'user'
HOST     = 'host'
PASSWORD = 'password'

def initialize_connection(db, usr, hst, pswd):
    #Setup DB Connection
    conn = psycopg2.connect(database=db, user=usr, host=hst, password=pswd)
    return conn.cursor()


### Function Definitions
#Define DB queries
def write(status, cursor):
    if status:
        transaction_status = '0'
    else:
        transaction_status = '1'
    raw_sql = "INSERT INTO transactionsimulation (tsn_tstate) VALUES (%(transaction_status));"
    cursor.execute(raw_sql)
    cursor.commit()

def write_dirty(cursor):
    write(False, cursor)

def write_clean(cursor):
    write(True, cursor)

#Define rolldice
def rolldice(thresh, cursor):
	if random.randrange(100) <= thresh:
		write_dirty(cursor)
		return 1
	else:
		write_clean(cursor)
		return 0

def main():
    cursor = initialize_connection(DATABASE, USER, HOST, PASSWORD)
    #main loop
    Ti = datetime.datetime.now()
    dT = datetime.timedelta(0,10)
    Tt = datetime.datetime.now() + datetime.timedelta(0,1200)

    #initiate main loop
    thresh = 25
    while datetime.datetime.now() < Tt:
        #main program function
        #thresh = 25
        rolldice(thresh, cursor)
        #if a == 0:
        #	thresh += 25
        #else:
        #	thresh = 25
        T0 = datetime.datetime.now()
        while datetime.datetime.now() < T0 + dT:
            continue

    conn.close()

if __name__ == '__main__':
    main()
