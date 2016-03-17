# My fork of <a href="https://github.com/jessedobbelaere/mysql-ssh-backups" target="_blank">this</a>

My changes to the original
- Database names are not entered in the config file, but generated dynamically from a sql query, the script backs up every database the query finds.
- SSH credentials can be entered globally or per website
- Backups are stored both on the server and locally, you define the directories in the config
- Old backups (local and server) are removed after X days - defined in the config
- Renamed a few things


# MySQL backups with Python & SSH

## Description
Backup the MySQL databases of all your hosted websites to your computer by using an SSH connection to the webserver.

## How to use it

1. Make sure you have `pip` & `python` installed
2. Install the paramiko package `sudo pip install paramiko`
3. Download or git clone the source files
4. Make sure that you can access your webserver by using SSH. You’ll need to make an SSH key.
  1. Copy the result of `cat ~/.ssh/id_rsa.pub`
  2. SSH to your server
  3. `vim ~/.ssh/authorized_keys`
  4. Paste the contents (your key) and save
  5. ctrl+d to exit
5. Open the `config/config.json.dist` and rename it to `config/config.json` and fill the details of your webserver and database credentials. You can add as many webservers/databases as you want!

        {
            "settings": {
                "backup_folder": "backup/"          /* The local backup folder */
            },
            "websites": {

                "name_firstwebsite": {
                    "config": {
                        "host": "",                 /* Webserver hostname */
                        "username": ""              /* Webserver username */
                    },
                    "databases": {
                        "database_examplename1": {
                            "mysql_host": "",       /* Mysql hostname */
                            "mysql_user": "",       /* Mysql username */
                            "mysql_pwd": ""         /* Mysql password */
                        }
                    }
                },

                "name_secondwebsite": {
                    ...
                }
            }
        }

6. Run `python backup-mysql-database-ssh.py` to backup your database or configure it to run periodically as a cronjob (OS X tip: [Lingon](https://www.peterborgapps.com/lingon/)). Using Lingon, create a new task, give it a name and let it execute `/usr/bin/python /Users/pathtoscript/backup-mysql-database-ssh.py` at e.g. every 12 hours.

## Bugs

If you encounter any bugs, please create an issue and I’ll try to fix it (or feel free to fix it yourself with a pull-request).

## Discussion
- Twitter: [@jessedobbelaere](https://www.twitter.com/jessedobbelaere)
- E-mail: <jesse@dobbelaere-ae.be> for any questions or remarks.
