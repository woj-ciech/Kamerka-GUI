# ꓘamerka GUI

## Ultimate Internet of Things/Industrial Control Systems reconnaissance tool.

### Powered by Shodan - Supported by Binary Edge & WhoisXMLAPI

writeup -
Demo - https://woj-ciech.github.io/kamerka-demo/kamerka.html

## Requirements
- python3
- django
- celery
- redis
- Shodan
- BinaryEdge
- WHOISXMLAPI
- Flickr
- Google Maps API

```pip3 install -r requirements.txt```

**Make sure your API keys are correct and put them in keys.json in main directory.**

## Run
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```
In a new window run celery worker
```celery -A kamerka --loglevel=info```

In a new window fire up redis
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

## Full list of supported devices with corresponding queries
```
"webcam": "device:webcam",
'printer': "device:printer",
'mqtt': 'product:mqtt',
'rtsp': "port:'554'",
'dicom': "dicom",
"ipcamera": "IPCamera_Logo",
"yawcam": "yawcam",
"blueiris": "http.favicon.hash:-520888198",
'ubnt': "UBNT Streaming Server",
"go1984": "go1984",
"dlink": "Server: Camera Web Server",
"avtech": "linux upnp avtech",
"adh": "ADH-web",

"niagara": "port:1911,4911 product:Niagara",
'bacnet': "port:47808",
'modbus': "port:502",
'siemens': 'Original Siemens Equipment Basic Firmware:',
'dnp3': "port:20000 source address",
"ethernetip": "port:44818",
"gestrip": 'port:18245,18246 product:"general electric"',
'hart': "port:5094 hart-ip",
'pcworx': "port:1962 PLC",
"mitsubishi": "port:5006,5007 product:mitsubishi",
"omron": "port:9600 response code",
"redlion": 'port:789 product:"Red Lion Controls"',
'codesys': "port:2455 operating system",
"iec": "port:2404 asdu address",
'proconos': "port:20547 PLC",

"plantvisor": "Server: CarelDataServer",
"iologik": "iologik",
"moxa": "Moxa",
"akcp": "Server: AKCP Embedded Web Server",
"spidercontrol": "powered by SpiderControl TM",
"tank": "port:10001 tank",
"iq3": "Server: IQ3",
"is2": "IS2 Web Server",
"vtscada": "Server: VTScada",
'zworld': "Z-World Rabbit 200 OK",
"nordex": "Jetty 3.1.8 (Windows 2000 5.0 x86) \"200 OK\" "
```

# Used components
- Background IoT photo by  https://unsplash.com/@pawel_czerwinski
- Background ICS photo by  https://unsplash.com/@wimvanteinde
- Joli admin template - https://github.com/sbilly/joli-admin
- Search form - Colorlib Search Form v15
- country picker - https://github.com/mojoaxel/bootstrap-select-country
- Multiselect - https://github.com/varundewan/multiselect/
- Arsen Zbidniakov Flat UI Checkbox https://codepen.io/ARS/pen/aeDHE/

# Known bugs:
- It's version 1.0 so please raise an issue if you think you found any bug or have an idea to make it better.
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
- I'm not responsible for any damage caused by use this tool.
