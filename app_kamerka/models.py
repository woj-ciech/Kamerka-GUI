from django.db import models
from jsonfield import JSONField


# Create your models here.


class Search(models.Model):
    coordinates = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    ics = models.CharField(max_length=100)
    coordinates_search = models.CharField(max_length=1000)
    nmap = models.BooleanField(default=False)

class Device(models.Model):
    search = models.ForeignKey(Search, on_delete=models.CASCADE)
    ip = models.CharField(max_length=100, default="")
    product = models.CharField(max_length=500, default="")
    org = models.CharField(max_length=100, default="", null=True)
    data = models.CharField(max_length=1000, default="")
    port = models.CharField(max_length=10, default="")
    type = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=100, default="", null=True)
    lon = models.CharField(max_length=100, default="")
    lat = models.CharField(max_length=100, default="")
    country_code = models.CharField(max_length=100, default="")
    query = models.CharField(max_length=100, default="")
    category = models.CharField(max_length=100, default="")
    vulns = models.CharField(max_length=100, default="")
    indicator = models.CharField(max_length=100, default="")
    hostnames = models.CharField(max_length=100, default="")
    screenshot = models.CharField(max_length=100000, default="")
    located = models.BooleanField(default=False, null=True)
    notes = models.CharField(max_length=1000, default="")


class DeviceNearby(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    lat = models.CharField(max_length=100)
    lon = models.CharField(max_length=100)
    ip = models.CharField(max_length=100)
    product = models.CharField(max_length=100)
    port = models.CharField(max_length=100)
    org = models.CharField(max_length=100)


class TwitterNearby(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    lat = models.CharField(max_length=100)
    lon = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    tweet = models.CharField(max_length=100)


class FlickrNearby(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    lat = models.CharField(max_length=100)
    lon = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    title = models.CharField(max_length=100)


class ShodanScan(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    ports = models.CharField(max_length=100)
    tags = models.CharField(max_length=100)
    products = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    vulns = models.CharField(max_length=100)


class BinaryEdgeScore(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    grades = JSONField()
    cve = JSONField()
    score = models.CharField(max_length=3)


class Whois(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    org = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    netrange = models.CharField(max_length=100)
    admin_org = models.CharField(max_length=100)
    admin_email = models.CharField(max_length=100)
    admin_phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
