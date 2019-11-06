"""
WSGI config for kamerka project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from app_kamerka.models import Device, Search, DeviceNearby

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kamerka.settings')

application = get_wsgi_application()
all_objects = DeviceNearby.objects.all().values()
# pl = Search.objects.filter().values()
# det = DeviceDetails.objects.filter().values()
# print(pl)
# print(all_objects)
# print(det)
