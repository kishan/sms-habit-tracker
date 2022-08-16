import os
from django.conf import settings
from habit_tracker.lib_twilio import send_sms
from users.models import User
from datetime import datetime

#
# this file contains all cron jobs which are scheduled via CRONJOBS in settings.py
#
# Make sure to run below command every time CRONJOBS in settings.py is changed in any way:
#   'python manage.py crontab add'
#
# to manually run cron: 'python manage.py crontab run <job_id>'
#   you can view all jobs via 'python manage.py crontab show'
#
# Debugging cron jobs:
# - you can view all current active jobs via 'python manage.py crontab show'
# - to manually run cron: 'python manage.py crontab run <job_id>'
# - you should be able to view cron logs with any errors at /var/mail/{user}
# - ensure right cron jobs are being added to crontab via 'crontab -e'
#

def cron_send_test_text():
    phone_number = settings.USER_TEST_NUMBER
    print('sending text via cron to: ' + phone_number)
    send_sms(phone_number, f"This is automated message via cron")
 
# log current time
def cron_log_time():
    # Ex. 2022-08-16 15:29:45
    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log_file_path = os.path.join(settings.LOGS_PATH, 'cron.log')
    with open(log_file_path, 'a+') as f: 
        data = 'django cron: ' + current_time
        f.write('\n' + data)