#!/bin/sh
#This script runs the gunicorn server

gunicorn server:app -w 4 --threads 2 -b 0.0.0.0:5000