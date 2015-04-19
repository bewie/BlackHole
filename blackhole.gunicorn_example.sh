#!/bin/bash


if [ "`whoami`" != "root"  ];then
    echo " It must run as root" # Or ensure thath the user who runs it has permissions to read the logs for download
    exit 1
fi
NAME="blackhole"                                  # Name of the application
DJANGODIR=/opt/BlackHole/          # Django project directory
USER=root                                    # the user to run as
GROUP=blackhole                                      # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=blackhole.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=blackhole.wsgi                     # WSGI module name
LOG=/var/log/blackhole/blackhole.log
BIND_IP=127.0.0.1
BIND_PORT=8001
echo "Starting $NAME"

# Activate the virtual environment
#cd $DJANGODIR
#source ../bin/activate
#export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
#export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
rm $LOG
cd $DJANGODIR
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-file=$LOG \
  --bind=$BIND_IP:$BIND_PORT
