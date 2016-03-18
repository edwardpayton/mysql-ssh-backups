import paramiko
import json
import datetime
import os

# SSH function to get the output from the server when the command is executed
def ssh(cmd):
    out = []
    msg = [stdin, stdout, stderr] = client.exec_command(cmd)
    for item in msg:
        try:
            for line in item:
                out.append(line.strip('\n'))
        except Exception, e:
            pass

    return list(out)


# Get current script directory
script_dir_path = os.path.dirname(os.path.realpath(__file__))

# Loading the configuration file
config_file = open(script_dir_path + "/config/config.json", "r")
config_file = json.load(config_file)

##
today = datetime.date.today()
date = str(today)
days = config_file['settings']['days_to_keep']
threshold = datetime.datetime.now() + datetime.timedelta(days = - days)

local_dir = config_file['settings']['local_dir']
local_backup_dir = local_dir + date

# Loop every website to backup
for w in config_file['websites']:

    # Remote directory
    remote_dir = config_file['websites'][w]['remote_dir']

    # SSH
    if config_file['websites'][w]['ssh']['use_default_ssh'] == False:
        ssh_user = config_file['websites'][w]['ssh']['ssh_user']
        ssh_host = config_file['websites'][w]['ssh']['ssh_host']
    else:
        ssh_user = config_file['settings']['default_ssh_user']
        ssh_host = config_file['settings']['default_ssh_host']

    # mySql
    sql_user = config_file['websites'][w]["mysql"]['mysql_user']
    sql_pass = config_file['websites'][w]["mysql"]['mysql_pwd']
    sql_host = config_file['websites'][w]["mysql"]['mysql_host']

    # Open SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(ssh_host, username=ssh_user)

    # Open SFTP connection
    sftp_client = client.open_sftp()

    # Database var
    databases = ssh("mysql -q -u " + sql_user + " -h " + sql_host + " -p" + sql_pass + " -e 'show databases;'")

    # Create remote backup folder (if not existing)
    if not os.path.exists(remote_dir + date):
        ssh('mkdir ' + remote_dir + date)
    remote_backup_dir = remote_dir + date

    # Create local backup folder (if not existing)
    if not os.path.exists(local_backup_dir):
        os.makedirs(local_backup_dir)

    # Loop the databases
    for db in databases:

        # File paths
        remote_file_path = remote_backup_dir + '/' + db + '.sql.bz2'
        local_file_path = local_backup_dir + '/' + db + '.sql.bz2'

        # Create backup file
        ssh('mysqldump -u' + sql_user + ' -p' + sql_pass + ' -h' + sql_host + ' ' + db + ' --lock-tables=false | bzip2 - - > ' + remote_file_path)

        # Open SFTP connection & download the backup file to the backup dir
        remote_file = sftp_client.get(remote_file_path, local_file_path)

    # Remove old backup files and folders (server)
    ssh('find ' + remote_dir + '* -type d -mtime +' + str(days) + ' -exec rm -r {} \;')

    # Close the connection
    client.close()

# Remove old backup files and folders (local)
for d in os.listdir(local_dir):
    absolute_d = os.path.join(local_dir, d)
    st = os.stat(absolute_d)
    mtime = datetime.datetime.fromtimestamp(st.st_mtime)

    if mtime < threshold:
        print('remove ' + d)

# Send Email
# count files
file_list = next(os.walk(local_backup_dir))[2]
number_files = len(file_list)
# list local files
files_arr = []
for f in file_list:
    f_path = local_backup_dir + '/' + f
    files_arr.append(f_path)
files_arr = '\n '.join(files_arr)
# prepare email
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

def send_mail(text,subject=""):

    msg = MIMEText(text)
    msg["From"] = "MySql Backup <e@mail.com>"
    msg["To"] = config_file['settings']['email']
    msg["Subject"] = "MySql Backup Report " + subject
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())


if number_files == 0:
    text = "Something went wrong, databases were not backed up."
    send_mail(text,"ERROR")
else:
    text = """\
%s databases were backed up on the server here:
%s

Backups stored locally:
%s\
    """ % (number_files, remote_backup_dir, files_arr)
    send_mail(text)
