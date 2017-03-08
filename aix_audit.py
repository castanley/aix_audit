#!/usr/local/bin/python2.7
import paramiko
import psycopg2
import time

date = (time.strftime("%m/%d/%Y"))

class bcolors:
    MAGENTA = '\033[95m'
    RED = '\033[93m'
    ENDC = '\033[0m'

def main():

    #Define our connection string
    conn_string = "host='REMOVED' dbname='billing' user='REMOVED' password='REMOVED' connect_timeout=3"

    # print the connection string we will use to connect
    #print bcolors.MAGENTA + 'Connecting to database\n    ->%s' % (conn_string) + bcolors.ENDC + "\n"

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    sql = conn.cursor()
    print bcolors.RED + "Inserting AIX information into database.\n" + bcolors.ENDC

    #key = paramiko.RSAKey.from_private_key_file("./key")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #Begin SSH connection
    ssh.connect('HMCSERVER', username='REMOVED', password='REMOVED')

    nodesp8 = ['p822-01','p822-02','p822-03','p822-04','P740-05']

    for device in nodesp8:
        stdin, stdout, stderr = ssh.exec_command("lshwres -r proc -m %s --level lpar -F \"lpar_name curr_procs\"" % device)
        result = stdout.readlines()
        #Host and CPU number List remove \n
        cpuNum = [item.rstrip() for item in result]

        for line in result:
            (name,units) = line.split()
            units = int(units) - 1

            if units != 0:
                cmd = "INSERT INTO obj_temp (rec_date, device, name, units, function_code) VALUES (%s, %s, %s, %s, %s);"
                data = (date, device, name, units, "UX40",)
                sql.execute(cmd, data)
                print "%s %s %s %s UX40" % (date, device, name, units)

            cmd = "INSERT INTO obj_temp (rec_date, device, name, units, function_code) VALUES (%s, %s, %s, %s, %s);"
            data = (date, device, name, 1, "UX10",)
            sql.execute(cmd, data)
            print "%s %s %s %s UX10" % (date, device, name, 1)

        stdin, stdout, stderr = ssh.exec_command("lshwres -r mem -m %s --level lpar -F \"lpar_name curr_mem\"" % device)
        result = stdout.readlines()
        #host and Memory usage List remove \n
        memNum = [item.rstrip() for item in result]

        for line in result:
            (name,units) = line.split()
            units = (((int(units) / 1024) - 2) / 2)

            cmd = "INSERT INTO obj_temp (rec_date, device, name, units, function_code) VALUES (%s, %s, %s, %s, %s);"
            data = (date, device, name, units, "UX30",)
            sql.execute(cmd, data)
            print "%s %s %s %s UX30" % (date, device, name, units)

    conn.commit()
    sql.close()
    conn.close()

    #print 'This is error =',stderr.readlines()

    #Close our SSH connection
    ssh.close()

if __name__ == "__main__":
    main()
