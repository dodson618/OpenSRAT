#! /usr/bin/python

### IMPORT MODULES
import psycopg2, time, datetime, smtplib, getpass, os, sys, glob, shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CONFIG_FILE = "reptest.config"

def load_config(config_file=CONFIG_FILE):
    """
    load_config checks <config_file> and loads variable declarations as a dictionary
    of "{VAR_NAME : VAR_VALUE}" construction
    """

    with open(config_file,"r") as c_file:
        config_out = c_file.read()

        config_out = config_out.split("\n")

        config = {}
        for i in range(len(config_out)):
            config_out[i] = config_out[i].replace(" ","",2)
            config[config_out[i][:config_out[i].find("=")]] = config_out[i][config_out[i].find("=")+1:]

        return config

try:
    config = load_config()
except:
    print "Check Config File..."
    sys.exit(1)

dT = datetime.timedelta(0,int(config['dT']))
WORK_DIR = config['WORK_DIR'].replace("'","").replace('"',"")
LOG_SUB = config['LOG_SUB'].replace("'","").replace('"',"")
LOG_DIR = WORK_DIR + LOG_SUB
LOG_NAME = config['LOG_NAME'].replace("'","").replace('"',"")
DATABASE = config['DATABASE'].replace("'","").replace('"',"")
USER = config['USER'].replace("'","").replace('"',"")
HOST = config['HOST'].replace("'","").replace('"',"")
PASSWORD = config['PASSWORD'].replace("'","").replace('"',"")
QUERY_SUBJECT = config['QUERY_SUBJECT'].replace("'","").replace('"',"")
QUERY_PREDICATE = config['QUERY_PREDICATE'].replace("'","").replace('"',"")
TO_EMAIL = config['TO_EMAIL'].replace("'","").replace('"',"")
FROM_EMAIL = config['FROM_EMAIL'].replace("'","").replace('"',"")
SEND_EMAIL_USER = config['SEND_EMAIL_USER'].replace("'","").replace('"',"")
SEND_EMAIL_PASSWORD = config['SEND_EMAIL_PASSWORD'].replace("'","").replace('"',"")
SUBJECT_NAME = config['SUBJECT_NAME'].replace("'","").replace('"',"")
LOG_HEADER = config['LOG_HEADER'].replace("'","").replace('"',"")
### DEFINE FUNCTIONS

## Time Logging Functions

def write_log(work_dir=WORK_DIR):
    """
    write_log logs current time as 'Last Run Time'
    """
    TimeLog = open(work_dir + "/time.log","w")
    T_N = datetime.datetime.now()
    TimeLog.write(str(T_N))
    TimeLog.close()


def read_log(work_dir=WORK_DIR):
    """
    read_log retrieves saved 'Last Run Time'
    """
    try:
        TimeLog = open(work_dir + "/time.log","r")
        T_LR = TimeLog.read()
        T_LR = datetime.datetime.strptime(T_LR[0:19], '%Y-%m-%d %H:%M:%S')
        TimeLog.close()
        if T_LR == None or len(str(T_LR)) < 19:
            print "WARNING! Time Last Run not found. Please Run Manual Reports"
            T_N = datetime.datetime.now()
            T_LR = datetime.datetime(T_N.year,T_N.month,T_N.day)
            print "Last Run Time set to: %s" % str(T_LR)
    except:
        print "WARNING! Time Last Run not found. Please Run Manual Reports"
        TimeLog = open(work_dir + "/time.log","w")
        T_N = datetime.datetime.now()
        T_LR = datetime.datetime(T_N.year, T_N.month, T_N.day)
        TimeLog.write(str(T_LR))
        print """Last Run Time set to: %s""" % str(T_LR)
        TimeLog.close()
    return T_LR


## Internal Time Functions
#def set_tnr(now=1, T_LR):
def set_tnr(T_LR, now=1, dT=dT):
    """
    set_tnr sets next run time
    """
    if now == 1:
        T_NR = datetime.datetime.now() + dT
    else:
        T_NR = T_LR + dT
    return T_NR


## Database Functions
def run_query(T_LR, db, usr, hst, pswd,query_subject=QUERY_SUBJECT,query_predicate=QUERY_PREDICATE):
    """
    run_query returns the results of the report query
    """
    q_var = """ > '%s'""" % T_LR
    query = query_subject + q_var + query_predicate
    conn = psycopg2.connect(database=db, user=usr, host=hst, password=pswd)
    cursor = conn.cursor()
    cursor.execute(query)
    q_result = cursor.fetchall()
    conn.commit()
    conn.close()
    return q_result

def send_results(T_LR, log_dir=LOG_DIR, to_email=TO_EMAIL, from_email=FROM_EMAIL, send_email_user=SEND_EMAIL_USER, send_email_password=SEND_EMAIL_PASSWORD, log_name=LOG_NAME, subject_name=SUBJECT_NAME):
    """
    SMTP Negotiation and sending (T_LR is used to attach a unique identifier as the subject)
    """
    sent_logs = log_dir + "/sent"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "%s: %s" % (subject_name, str(T_LR)[:19])
    os.chdir(log_dir)
    filenames = glob.glob("*"+log_name)
    for i in filenames:
        with file(i) as fp:
            attachment = MIMEText(fp.read())
            attachment.add_header('Content-Disposition','attachment',filename=i)
            msg.attach(attachment)
    if len(filenames) > 0:
        s = smtplib.SMTP("smtp.gmail.com",587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(send_email_user,send_email_password)
        s.sendmail(msg['From'],msg['To'].split(","),msg.as_string())
        s.close()


## Miscellaneous Service Scripts
def sav_res(T_LR,res,log_dir=LOG_DIR,log_name=LOG_NAME, log_header=LOG_HEADER):
    """
    sav_res() commits query results to a log file
     of the following name : "YYYY-MM-DD HH:MM:SS - <log_name>" in ./logs
    """
    if len(res) > 0:
        #Fix Tuples to Assemble output file
        for i in range(len(res)):
            try:
                res[i] = list(res[i])
            except:
                continue
        #Define file name, header
        ### REFACTOR header
        out_name = log_dir + "/" + str(T_LR)[:19].replace(":","") + " - " + log_name
        #Open File, Insert Results
        with open(out_name,"w") as fp:
            fp.write(log_header)
            for i in res:
                s = "%s,'%s',\n" % (i[0],i[1])
                fp.write(s)
    # REFACTOR THIS. if len(res) < 0 you don't get any useful information.

# Log Management (put away files already sent)
def mk_sent(log_dir=LOG_DIR,log_name=LOG_NAME):
    ## REFACTOR THIS... USE GLOBALS
    sent_logs = log_dir + "/sent"
    os.chdir(log_dir)
    f = glob.glob("*"+ log_name)
    for i in f:
        shutil.move(i,sent_logs)


#### Here starts the action.

### REFACTOR THIS.... if __name__ == '__main__': like the other file.
def main():
    # Get T_LR from log if exists
    T_LR = read_log()
    # Initialize Next Run based on last-run.
    T_NR = set_tnr(T_LR,0)

    #### START MAIN LOOP

    ###Refactoring largely done.
    TTerminal = datetime.datetime.now() + datetime.timedelta(0,600)
    while datetime.datetime.now() < TTerminal:
        #Get query results
        print "running the query"
        res = run_query(T_LR, DATABASE, USER, HOST, PASSWORD)
        #Save T_LR in log
        print "writing logs"
        write_log()
        #Set new T_NR
        print "set new T_NR"
        T_NR = set_tnr(T_LR)
        #Refresh T_LR from log
        print "refresh T_LR"
        T_LR = read_log()
        #Save Results
        print "sav_res"
        sav_res(T_LR,res)
        ### Send results via email
        #print "trying to send"
        try:
            #print "Not actually sending results..."
            print "send_results"
            send_results(T_LR)
            #print "Not Marking Sent"
            print "mk_sent"
            mk_sent()
        except:
            print "Send Failed"
            continue
        print "Waiting " + str(dT.total_seconds()) + "s"
        while datetime.datetime.now() < T_NR:
            time.sleep(5)

if __name__ == '__main__':
    main()
