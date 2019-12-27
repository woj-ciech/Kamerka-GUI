# ꓘamerka GUI

## Ultimate Internet of Things/Industrial Control Systems reconnaissance tool.

### Powered by Shodan - Supported by Binary Edge & WhoisXMLAPI

writeup - https://medium.com/@woj_ciech/hack-the-planet-with-%EA%93%98amerka-gui-ultimate-internet-of-things-industrial-control-systems-5ff7d9686b29   
Demo - https://woj-ciech.github.io/kamerka-demo/kamerka.html

## Update 15-11.2019 - Maritime support
https://twitter.com/the_wojciech/status/1195381924098904065

## Update 24-11.2019 - NMEA support
https://twitter.com/the_wojciech/status/1198598585182494720

## Update 01-12-2019 - Axis, RDP, VNC, Screenshot support
https://twitter.com/the_wojciech/status/1201159932499963905

## Update 11-12-2019 - Lots of new devices
https://twitter.com/the_wojciech/status/1204774550241722368

## Requirements
- beautiful soup
- python3
- django
- pynmea2
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
In a new window (in main directory) run celery worker
```celery worker -A kamerka --loglevel=info```

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
"webcamxp":"webcamxp",
"vivotek":"vivotek",
"techwin":"techwin",
"mobotix":"mobotix",
"iqinvision":"iqinvision",
"grandstream":"Grandstream",
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
"axis":'http.title:"axis" http.html:live',
"rdp":"has_screenshot:true port:3389",
"vnc":"has_screenthos:true port:5901",
"screenshot":"has_screenshot:true !port:3389 !port:3388 !port:5900",

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
'zworld': "Z-World Rabbit",
"nordex": "Jetty 3.1.8 (Windows 2000 5.0 x86)",

"axc":"PLC Type: AXC",
"modicon":"modicon",
"xp277":"HMI, XP277",
"vxworks":"vxworks",
"eig":"EIG Embedded Web Server",
"digi":"TransPort WR21",
"windweb":"server: WindWeb",
"moxahttp":"MoxaHttp",
"lantronix":"lantronix",
"entelitouch":"Server: DELTA enteliTOUCH",
"energyict_rtu":"EnergyICT RTU",
"crestron":"crestron",
"wince":'Server: "Microsoft-WinCE"',
"ipc@chip":"IPC@CHIP",
"addup":"addUPI",
"anybus":'"anybus-s"',
"windriver":"WindRiver-WebServer",
"wago":"wago",
"niagara_audit":"niagara_audit",
"niagara_web_server":"Niagara Web Server",
"trendnet":"trendnet",
"stulz_klimatechnik":"Stulz GmbH Klimatechnik",
"somfy":"title:Somfy",
"scalance":"scalance",
"simatic":"simatic",
"simatic_s7":"Portal0000",
"schneider_electric":"Schneider Electric",
"power_measurement":"Power Measurement Ltd",
"power_logic":"title:PowerLogic",
"telemecanique_bxm":"TELEMECANIQUE BMX",
"schneider_web":"Schneider-WEB",
"fujitsu_serverview":"serverview",
"eiportal":"eiPortal",
"ilon":"i.LON",
"Webvisu":"Webvisu",
"total_access": 'ta gen3 port:2000'

Medical
"zoll":"http.favicon.hash:-236942626",
"perioperative":"HoF Perioperative",
"wall_of_analytics":"title:'Wall of Analytics'",
"viztek_exa":"X-Super-Powered-By: VIZTEK EXA",
"desert_view_bkup":"title:'DESERT VIEW BKUP'",
"intuitim":"http.favicon.hash:159662640",
"Medcon Archiving System":"http.favicon.hash:-897903496",
"orthanc_explorer":"title:'Orthanc Explorer'",
"Marco Pacs":"title:'Marco pacs'", 
"osirix":"title:OsiriX",
"clari_pacs":"title:ClariPACS",
"siste_lab":"http.html:SisteLAB",
"opalweb":"html:opalweb",
"neuropro":"title:'EEG Laboratory'",
"tmw_document_imaging":"title:'TMW Document Imaging'",
"erez":"title:'eRez Imaging'",
"gluco_care":"html:'GlucoCare igc'",
"glucose_guide":"title:'glucose guide'",
"grandmed_glucose":"title:'Grandmed Glucose'",
"philips_digital_pathology":"title:'Philips Digital Pathology'",
"tricore_pathology":"title:'TriCore Pathology'",
"appsmart_ophthalmology":"title:'Appsmart Ophthalmology'",
"chs_ophthalmology":"title:'CHS Ophthalmology'",
"ram_soft":"html:powerreader",
"xnat":"http.favicon.hash:-230640598",
"iris_emr":"title:'Iris EMR'",
"eclinicalworks_emr":"title:'Web EMR Login Page'",
"open_emr":"http.favicon.hash:1971268439",
"oscar_emr":"title:'OSCAR EMR'",
"wm_emr":"http.favicon.hash:1617804812",
"doctors_partner_emr":"title:'DoctorsPartner'",
"mckesson_radiology":"title:'McKesson Radiology'",
"kodak_carestream":"title:'Carestream PACS'",
"meded":"title:meded",
"centricity_radiology":"http.favicon.hash:-458315012",
"openeyes":"http.favicon.hash:-885931907",
"orthanc":"orthanc",
"horos":"http.favicon.hash:398467600"
"open_mrs":"title:openmrs",
"mirth_connect":"http.favicon.hash:1502215759",
"acuity_logic":"title:AcuityLogic",
"optical_coherence_tomography":"title:'OCT Webview'",
"philips_intellispace":"title:INTELLISPACE",
"vitrea_intelligence":"title:'Vitrea intelligence'",
"phenom_electron_microscope":"title:'Phenom-World'",
"meddream_dicom_viewer":"html:Softneta",
"merge_pacs":"http.favicon.hash:-74870968",
"synapse_3d":"http.favicon.hash:394706326",
"navify":"title:navify",
"telemis_tmp":"http.favicon.hash:220883165",
"brainlab":"title:'Brainlab Origin Server'",
"nexus360":"http.favicon.hash:125825464",
"brain_scope":"title:BrainScope",
"omero_microscopy":"http.favicon.hash:2140687598",
"meditech":"Meditech",
"cynetics":"cynetics",
"promed":"Promed",
"carestream":"Carestream",
"carestream_web":"title:Carestream",
"vet_rocket":"http.html:'Vet Rocket'",
"planmeca":"Planmeca",
"vet_view":"http.favicon.hash:1758472204",
"lumed":"http.html:'LUMED'",
"infinitt":"http.favicon.hash:-255936262",
"labtech":"labtech",
"progetti":"http.html:'Progetti S.r.l.'",
"qt_medical":"http.html:'QT Medical'",
"aspel":"ASPEL",
"huvitz_optometric":"http.html:'Huvitz'",
"optovue":"Optovue",
"optos_advance":"http.title:'OptosAdvance'",
"asthma_monitoring_adamm":"http.title:'HCO Telemedicine'",
"pregnabit":"http.html:'Pregnabit'",
"prime_clinical_systems":"http.html:'Prime Clinical Systems'",
"omni_explorer":"http.title:OmniExplorer",
"avizia":"http.html:'Avizia'",
"operamed":"Operamed",
"early_sense":"http.favicon.hash:-639764351",
"tunstall":"http.html:'Tunstall'",
"clini_net":"http.html:'CliniNet®'",
"intelesens":"title:'zensoronline)) - online monitoring'",
"kb_port":"http.html:'KbPort'",
"nursecall_message_service":"http.title:'N.M.S. - Nursecall Message Service'",
"image_information_systems":"http.html:'IMAGE Information Systems'",
"agilent_technologies":"Agilent Technologies port:5025",
"praxis_portal2":"http.html:'Medigration'",
"xero_viewer":"http.title:'XERO Viewer'"

Excluded:
title:"pacemaker-id"
html:klinikinew
title:"EEG Viewer"
http.favicon.hash:-1989988507
plexus platenet
http.favicon.hash:-189701579
title:"Insulin Dosage"
pathology image seve
http.favicon.hash:538032019
title:"MsFLASH"
title:"THIP EMR"
title:"CARDIOHF"
title:"CN EMR Office"
Power2Practice
http.favicon.hash:-1982401487
Cosmed EMR
http.favicon.hash:-1747178511
title:" Premier Radiology synapse"
title:"PRIME - Electrical Resistivity Tomography"
title:"OCT II System"
http.favicon.hash:-582594220
title:"Atomic Force Microscope"
title:axeda
http.favicon.hash:-1351683412
title:"InTouch Health Log Manager"
title:"Pharma Vtiger"
title:sema4
NAVIFY
Nextech
http.html:'Radiometer Medical '
HeartStart
http.favicon.hash:-893361748
```

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
- I'm not responsible for any damage caused by using this tool.
