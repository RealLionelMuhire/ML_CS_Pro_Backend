#!/usr/bin/env bash

# Exit on first error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
./manage.py collectstatic --noinput

