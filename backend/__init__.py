from __future__ import absolute_import, unicode_literals

# backend/__init__.py

default_app_config = 'backend.apps.BackendConfig'

# Import celery app to ensure it is loaded when Django starts
from ML_CS_Pro_Backend.celery import app as celery_app

__all__ = ('celery_app',)
