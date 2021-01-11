# ꓘamerka GUI

## Ultimate Internet of Things/Industrial Control Systems reconnaissance tool.

### Powered by Shodan - Supported by Binary Edge & WhoisXMLAPI

writeup -https://www.offensiveosint.io/hack-the-planet-with-amerka-gui-ultimate-internet-of-things-industrial-control-systems-reconnaissance-tool/

https://www.offensiveosint.io/hack-like-its-2077-presenting-amerka-mobile/


Demo - https://woj-ciech.github.io/kamerka-demo/kamerka.html

## Update 15-11.2019 - Maritime support
https://twitter.com/the_wojciech/status/1195381924098904065

## Update 24-11.2019 - NMEA support
https://twitter.com/the_wojciech/status/1198598585182494720

## Update 01-12-2019 - Axis, RDP, VNC, Screenshot support
https://twitter.com/the_wojciech/status/1201159932499963905

## Update 11-12-2019 - Lots of new devices
https://twitter.com/the_wojciech/status/1204774550241722368

## Update 27-12-2019 - Added medical devices
https://medium.com/@woj_ciech/when-%EA%93%98amerka-meets-healthcare-research-on-exposed-medical-devices-ac62f2840da4

## Update 20.01.2020 - New device & mobile support
https://medium.com/@woj_ciech/hack-like-its-2077-presenting-%EA%93%98amerka-mobile-8886bc2680bf

## Update 23-01.2020 - NMAP scan upload update
To make this work you need to download database "GeoLite2-City.mmdb" (binary format) from MaxMind https://dev.maxmind.com/geoip/geoip2/geolite2/ and put it in root directory of project
https://twitter.com/the_wojciech/status/1220436310302887938

## Update 11.01.2021 - Added Scan & Exploit & Information & Default passwords
Added possibility to scan all devices with NMAP and NSE for ICS devices.
Added exploits for IoT and ICS devices.
Added information about devices and default credentials.

## Requirements
- beautiful soup
- python3
- django
- pynmea2
- celery
- redis
- Shodan paid account
- BinaryEdge (Optional)
- WHOISXMLAPI (Optional)
- Flickr (Optional)
- Google Maps API
- Pastebin PRO (Optional)
- xmltodict
- python-libnmap

```pip3 install -r requirements.txt```

**Make sure your API keys are correct and put them in keys.json in main directory.**

## Run
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```
In a new window (in main directory) run celery worker
```celery worker -A kamerka --loglevel=info```

For new version of Celery
```celery --app kamerka worker```

In a new window fire up redis
```apt-get install redis```
```redis-server```

And server should be available on ```https://localhost:8000/```


# Search
## Search for Industrial Control Devices in specific country
 ![](https://i.imgur.com/8qx5X3l.jpg)

- "All results" checkbox means get all results from Shodan, if it's turned off - only first page (100) results will be downloaded.
- "Own database" checkbox does not work but shows that is possible to integrate your own geolocation database. Let me know if you have access to better than Shodan's default one.

## Search for Internet of things in specific coordinates
Type your coordinates in format "lat,lon", hardcoded radius is 20km.
  ![](https://i.imgur.com/dSo4Kg0.jpg)


# Dashboard
   ![](https://i.imgur.com/H0cQJVY.jpg)

# Maps
## Los Angeles map
 ![](https://i.imgur.com/Oq9ZTBn.jpg)

## Industrial Control Systems in Canada
![](https://i.imgur.com/Z8xfHkB.jpg)

# Device map & details
![](https://i.imgur.com/M7V4IAq.jpg)

# Intel
![](https://www.offensiveosint.io/content/images/2021/01/csu-1.png)

# Scan & Exploit & Information
![](https://www.offensiveosint.io/content/images/2021/01/s7.png)

![](https://www.offensiveosint.io/content/images/2021/01/bosz3.png)


## Full list of supported devices with corresponding queries
https://github.com/woj-ciech/Kamerka-GUI/blob/master/queries.md


# Used components
- Background IoT photo by https://unsplash.com/@pawel_czerwinski
- Background ICS photo by https://unsplash.com/@wimvanteinde
- Background Healthcare photo by Arseny Togulev - https://unsplash.com/@tetrakiss 
- Joli admin template - https://github.com/sbilly/joli-admin
- Search form - Colorlib Search Form v15
- country picker - https://github.com/mojoaxel/bootstrap-select-country
- Multiselect - https://github.com/varundewan/multiselect/
- Arsen Zbidniakov Flat UI Checkbox https://codepen.io/ARS/pen/aeDHE/
- icon from icons8.com and icon-icons.com
- Nmap Scripts from NMAP Script Engine and Digital Bond repository
- Exploits from exploit-db and routersploit

# Known bugs:
- Sometimes search page keeps the last values, so please use ctrl+shift+R to refresh the main search page
- Debug info is left on purpose for raising an issues
- still some problems with getting cves from shodan search results
- Flickr infowindow size

# Contribution
I really care about feedback from you. If you have any idea how to make tool better, I'm more than happy to hear it.
It's also possible to upload and host the tool online, if you want to help, dm me.

# TODO
- Live monitoring
- Offensive capabilities 
- More devices 
- More sources (Instagram?, Youtube?)
- Integration with Nmap and plcscan
- Extensive error checking/debugging
- Cleanup code, delete legacy/unused dependencies js, css files
- Keeping keys in db
- Your ideas

# Remarks
- Tested only on Kali Linux 2019.3
- It uses default sqlite Django database
- Buttons in Intel tab for device do not show the progress bars, you have a results in max couple of seconds.
- Own database button does not work, it shows that it's possible to load your own geolocation database. I haven't found better than Shodan's but let me know if you have access to one.
- Looking for nearby Tweets works but I wasn't able to find any tweets. It may be a problem with Twitter API. Let me know if you can find anything.
- Don't blame me for unintentional bug that might exhaust your Shodan/BinaryEdge/WHOISXMLAPI credits.
- I'm not responsible for any damage caused by using this tool.
