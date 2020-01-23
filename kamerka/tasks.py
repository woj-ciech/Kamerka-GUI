import json
import math

import maxminddb
from libnmap.parser import NmapParser
import os

import flickrapi
import requests
from celery import shared_task, current_task
from celery_progress.backend import ProgressRecorder
from pybinaryedge import BinaryEdge
from shodan import Shodan
from twitter import *
import time
from bs4 import BeautifulSoup
import pynmea2
import base64

import urllib.parse
import urllib.request
import xml.etree.ElementTree as et

from app_kamerka.models import Device, DeviceNearby, Search, TwitterNearby, FlickrNearby, ShodanScan, BinaryEdgeScore, \
    Whois

healthcare_queries = {"zoll": "http.favicon.hash:-236942626",
                      'dicom': "dicom",
                      "perioperative": "HoF Perioperative",
                      "wall_of_analytics": "title:'Wall of Analytics'",
                      "viztek_exa": "X-Super-Powered-By: VIZTEK EXA",
                      "medweb": "html:'DBA Medweb. All rights reserved.'",
                      "intuitim": "http.favicon.hash:159662640",
                      "medcon_archiving_system": "http.favicon.hash:-897903496",
                      "orthanc_explorer": "title:'Orthanc Explorer'",
                      "Marco Pacs": "title:'Marco pacs'",
                      "osirix": "title:OsiriX",
                      "clari_pacs": "title:ClariPACS",
                      "siste_lab": "http.html:SisteLAB",
                      "opalweb": "html:opalweb",
                      "neuropro": "title:'EEG Laboratory'",
                      "tmw_document_imaging": "title:'TMW Document Imaging'",
                      "erez": "title:'eRez Imaging'",
                      "gluco_care": "html:'GlucoCare igc'",
                      "glucose_guide": "title:'glucose guide'",
                      "grandmed_glucose": "title:'Grandmed Glucose'",
                      "philips_digital_pathology": "title:'Philips Digital Pathology'",
                      "tricore_pathology": "title:'TriCore Pathology'",
                      "appsmart_ophthalmology": "title:'Appsmart Ophthalmology'",
                      "chs_ophthalmology": "title:'CHS Ophthalmology'",
                      "ram_soft": "html:powerreader",
                      "xnat": "http.favicon.hash:-230640598",
                      "iris_emr": "title:'Iris EMR'",
                      "eclinicalworks_emr": "title:'Web EMR Login Page'",
                      "open_emr": "http.favicon.hash:1971268439",
                      "oscar_emr": "title:'OSCAR EMR'",
                      "wm_emr": "http.favicon.hash:1617804812",
                      "doctors_partner_emr": "title:'DoctorsPartner'",
                      "mckesson_radiology": "title:'McKesson Radiology'",
                      "kodak_carestream": "title:'Carestream PACS'",
                      "meded": "title:meded",
                      "centricity_radiology": "http.favicon.hash:-458315012",
                      "openeyes": "http.favicon.hash:-885931907",
                      "orthanc": "orthanc",
                      "horos": "http.favicon.hash:398467600",
                      "open_mrs": "title:openmrs",
                      "mirth_connect": "http.favicon.hash:1502215759",
                      "acuity_logic": "title:AcuityLogic",
                      "optical_coherence_tomography": "title:'OCT Webview'",
                      "philips_intellispace": "title:INTELLISPACE",
                      "vitrea_intelligence": "title:'Vitrea intelligence'",
                      "phenom_electron_microscope": "title:'Phenom-World'",
                      "meddream_dicom_viewer": "html:Softneta",
                      "merge_pacs": "http.favicon.hash:-74870968",
                      "synapse_3d": "http.favicon.hash:394706326",
                      "navify": "title:navify",
                      "telemis_tmp": "http.favicon.hash:220883165",
                      "brainlab": "title:'Brainlab Origin Server'",
                      "nexus360": "http.favicon.hash:125825464",
                      "brain_scope": "title:BrainScope",
                      "omero_microscopy": "http.favicon.hash:2140687598",
                      "meditech": "Meditech",
                      "cynetics": "cynetics",
                      "promed": "Promed",
                      "carestream": "Carestream",
                      "carestream_web": "title:Carestream",
                      "vet_rocket": "http.html:'Vet Rocket'",
                      "planmeca": "Planmeca",
                      "vet_view": "http.favicon.hash:1758472204",
                      "lumed": "http.html:'LUMED'",
                      "infinitt": "http.favicon.hash:-255936262",
                      "labtech": "labtech",
                      "progetti": "http.html:'Progetti S.r.l.'",
                      "qt_medical": "http.html:'QT Medical'",
                      "aspel": "ASPEL",
                      "huvitz_optometric": "http.html:'Huvitz'",
                      "optovue": "Optovue",
                      "optos_advance": "http.title:'OptosAdvance'",
                      "asthma_monitoring_adamm": "http.title:'HCO Telemedicine'",
                      "pregnabit": "http.html:'Pregnabit'",
                      "prime_clinical_systems": "http.html:'Prime Clinical Systems'",
                      "omni_explorer": "http.title:OmniExplorer",
                      "avizia": "http.html:'Avizia'",
                      "operamed": "Operamed",
                      "early_sense": "http.favicon.hash:-639764351",
                      "tunstall": "http.html:'Tunstall'",
                      "clini_net": "http.html:'CliniNet®'",
                      "intelesens": "title:'zensoronline)) - online monitoring'",
                      "kb_port": "http.html:'KbPort'",
                      "nursecall_message_service": "http.title:'N.M.S. - Nursecall Message Service'",
                      "image_information_systems": "http.html:'IMAGE Information Systems'",
                      "agilent_technologies": "Agilent Technologies port:5025",
                      "praxis_portal2": "http.html:'Medigration'",
                      "xero_viewer": "http.title:'XERO Viewer'"}

ics_queries = {"niagara": "port:1911,4911 product:Niagara",
               'bacnet': "port:47808",
               'modbus': "port:502",
               'siemens': 'Original Siemens Equipment Basic Firmware:',
               'dnp3': "port:20000 source address",
               "ethernetip": "port:44818 Product name",
               "gestrip": 'port:18245,18246 product:"general electric"',
               'hart': "port:5094 hart-ip",
               'pcworx': "port:1962 PLC",
               "mitsubishi": "port:5006,5007 product:mitsubishi",
               "omron": "port:9600 response code",
               "redlion": 'port:789 product:"Red Lion Controls"',
               'codesys': 'product:"3S-Smart Software Solutions"',
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
               "nordex": "Jetty 3.1.8 (Windows 2000 5.0 x86) \"200 OK\" ",
               "sailor": "http.favicon.hash:-1222972060",
               'nmea': "$GPGGA",

               "axc": "PLC Type: AXC",
               "modicon": "modicon",
               "xp277": "HMI, XP277",
               "vxworks": "vxworks",
               "eig": "EIG Embedded Web Server",
               "digi": "TransPort WR21",
               "windweb": "server: WindWeb",
               "moxahttp": "MoxaHttp",
               "lantronix": "lantronix",
               "entelitouch": "Server: DELTA enteliTOUCH",
               "energyict_rtu": "EnergyICT RTU",
               "crestron": "crestron",
               "saphir": 'Server: "Microsoft-WinCE" "Content-Length: 12581"',
               "ipc@chip": "IPC@CHIP",
               "addup": "addUPI",
               "anybus": '"anybus-s"',
               "windriver": "WindRiver-WebServer",
               "wago": "wago",
               "niagara_audit": "niagara_audit",
               "niagara_web_server": "Niagara Web Server",
               "trendnet": "trendnet",
               "stulz_klimatechnik": "Stulz GmbH Klimatechnik",
               "somfy": "title:Somfy",
               "scalance": "scalance",
               "simatic": "simatic",
               "simatic_s7": "Portal0000",
               "schneider_electric": "Schneider Electric",
               "power_measurement": "Power Measurement Ltd",
               "power_logic": "title:PowerLogic",
               "telemecanique_bxm": "TELEMECANIQUE BMX",
               "schneider_web": "Schneider-WEB",
               "fujitsu_serverview": "serverview",
               "eiportal": "eiPortal",
               "ilon": "i.LON",
               "webvisu": "Webvisu",
               "total_access": 'ta gen3 port:2000',
               "vantage_infusion": "http.html:'InFusion Controller'",
               "sensoteq": "title:'sensoteq'",
               "sicon-8": "sicon-8",
               "automation_direct_hmi": "Server: EA-HTTP/1.0",
               "flotrac": "FloTrac",
               "innotech_bms": "http.title:'Innotech BMS'",
               "skylog": "http.title:skylog",
               "miele@home": "title:Miele@home",
               "alphacom": "http.title:Alphacom",
               "simplex_grinnell": "http.html:SimplexGrinnell title:login",
               "bosch_security": "http.html:'Bosch Security'",

               "fronius": "title:fronius",
               "webview": "http.favicon.hash:207964650",
               "Siemens Sm@rtClient": "title:'Siemens Sm@rtClient'",
               "WAGO": "title:'wago ethernet'",
               "sensatronics": "html:sensatronics",
               "extron": "Extron Electronics",
               "mikrotik_streetlighs": "mikrotik streetlight",
               "kesseltronics": "Kesseltronics",
               "unitronics": "title:'Unitronics PLC'",
               "atvise": "Server: atvise",
               "clearSCADA": "ClearSCADA",
               "youless": "title:YouLess",
               "DLILPC": "DLILPC",
               "intelliSlot": "title:IntelliSlot",
               "temperature_monitor": "title:'Temperature Monitor' !title:avtech",
               "CirCarLife": "CirCarLife",
               "web_scada": "title:'web scada'",
               "kaco": "kaco",
               "indect_parkway": "title:indect",
               "intuitive_Controller": "http.favicon.hash:1434282111",
               "intuitive_controller_2": "http.favicon.hash:-1011909571",
               "homeLYnk": "homeLYnk",
               "APC": "Location: home.htm Content-Length: 0 WebServer",
               "netio": "title:netio",
               "asi_controls": "title:'ASI Controls'",
               "myscada": "title:myscada",
               "iB-COM": "title:iB-COM",
               "building_operation_webstation": "title:'building operation'",
               "ftp_scada": "scada login",
               "apc_ftp": "APC FTP server",
               "network_management_card": "Network Management Card",
               "wemo_insight": "Belkin WeMo",
               "connect_ups": "title:ConnectUPS",
               "upshttpd": "Server: upshttpd",
               "poweragent": "PowerAgent",
               "CS121": "title:'CS121 SNMP/Web Adapter'",
               }

coordinates_queries = {"webcam": "device:webcam",
                       "webcamxp": "webcamxp",
                       "vivotek": "vivotek",
                       "techwin": "techwin",
                       "mobotix": "mobotix",
                       "iqinvision": "iqinvision",
                       "grandstream": "Grandstream",
                       'printer': "device:printer",
                       'mqtt': 'product:mqtt',
                       'rtsp': "port:'554'",
                       "ipcamera": "IPCamera_Logo",
                       "yawcam": "yawcam",
                       "blueiris": "http.favicon.hash:-520888198",
                       'ubnt': "UBNT Streaming Server",
                       "go1984": "go1984",
                       "dlink": "Server: Camera Web Server",
                       "avtech": "linux upnp avtech",
                       "adh": "ADH-web",
                       "axis": 'http.title:"axis" http.html:live',
                       "rdp": "has_screenshot:true port:3389",
                       "vnc": "has_screenthos:true port:5901",
                       "screenshot": "has_screenshot:true !port:3389 !port:3388 !port:5900",
                       "bbvs": "Server: BBVS",
                       "baudisch": "http.favicon.hash:746882768",
                       "loxone_intercom": "title:'Loxone Intercom Video'",

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

                       "axc": "PLC Type: AXC",
                       "modicon": "modicon",
                       "xp277": "HMI, XP277",
                       "vxworks": "vxworks",
                       "eig": "EIG Embedded Web Server",
                       "digi": "TransPort WR21",
                       "windweb": "server: WindWeb",
                       "moxahttp": "MoxaHttp",
                       "lantronix": "lantronix",
                       "entelitouch": "Server: DELTA enteliTOUCH",
                       "energyict_rtu": "EnergyICT RTU",
                       "crestron": "crestron",
                       "wince": 'Server: "Microsoft-WinCE"',
                       "ipc@chip": "IPC@CHIP",
                       "addup": "addUPI",
                       "anybus": '"anybus-s"',
                       "windriver": "WindRiver-WebServer",
                       "wago": "wago",
                       "niagara_audit": "niagara_audit",
                       "niagara_web_server": "Niagara Web Server",
                       "trendnet": "trendnet",
                       "stulz_klimatechnik": "Stulz GmbH Klimatechnik",
                       "somfy": "title:Somfy",
                       "scalance": "scalance",
                       "simatic": "simatic",
                       "simatic_s7": "Portal0000",
                       "schneider_electric": "Schneider Electric",
                       "power_measurement": "Power Measurement Ltd",
                       "power_logic": "title:PowerLogic",
                       "telemecanique_bxm": "TELEMECANIQUE BMX",
                       "schneider_web": "Schneider-WEB",
                       "fujitsu_serverview": "serverview",
                       "eiportal": "eiPortal",
                       "ilon": "i.LON",
                       "Webvisu": "Webvisu",
                       "total_access": 'ta gen3 port:2000',
                       "vantage_infusion": "http.html:'InFusion Controller'",
                       "sensoteq": "title:'sensoteq'",
                       "sicon-8": "sicon-8",
                       "automation_direct_hmi": "Server: EA-HTTP/1.0",
                       "flotrac": "FloTrac",
                       "innotech_bms": "http.title:'Innotech BMS'",
                       "skylog": "http.title:skylog",
                       "miele@home": "title:Miele@home",
                       "alphacom": "http.title:Alphacom",
                       "simplex_grinnell": "http.html:SimplexGrinnell title:login",
                       "bosch_security": "http.html:'Bosch Security'",

                       "fronius": "title:fronius",
                       "webview": "http.favicon.hash:207964650",
                       "siemens_Sm@rtClient": "title:'Siemens Sm@rtClient'",
                       "WAGO": "title:'wago ethernet'",
                       "sensatronics": "html:sensatronics",
                       "extron": "Extron Electronics",
                       "mikrotik_streetlighs": "mikrotik streetlight",
                       "kesseltronics": "Kesseltronics",
                       "unitronics": "title:'Unitronics PLC'",
                       "atvise": "Server: atvise",
                       "clearSCADA": "ClearSCADA",
                       "youless": "title:YouLess",
                       "DLILPC": "DLILPC",
                       "intelliSlot": "title:IntelliSlot",
                       "temperature_monitor": "title:'Temperature Monitor' !title:avtech",
                       "CirCarLife": "CirCarLife",
                       "web_scada": "title:'web scada'",
                       "kaco": "kaco",
                       "indect_parkway": "title:indect",
                       "intuitive_Controller": "http.favicon.hash:1434282111",
                       "intuitive_controller_2": "http.favicon.hash:-1011909571",
                       "homeLYnk": "homeLYnk",
                       "APC": "Location: home.htm Content-Length: 0 WebServer",
                       "netio": "title:netio",
                       "asi_controls": "title:'ASI Controls'",
                       "myscada": "title:myscada",
                       "iB-COM": "title:iB-COM",
                       "building_operation_webstation": "title:'building operation'",
                       "ftp_scada": "scada login",

                       "apc_ftp": "APC FTP server",
                       "network_management_card": "Network Management Card",
                       "wemo_insight": "Belkin WeMo",
                       "connect_ups": "title:ConnectUPS",
                       "upshttpd": "Server: upshttpd",
                       "poweragent": "PowerAgent",
                       "CS121": "title:'CS121 SNMP/Web Adapter'",

                       }


def get_keys():
    try:
        with open('keys.json') as keys:
            keys_json = json.load(keys)

        return keys_json
    except Exception as e:
        print(e)


keys = get_keys()


@shared_task(bind=False)
def devices_nearby(lat, lon, id, query):
    SHODAN_API_KEY = keys['keys']['shodan']

    device = Device.objects.get(id=id)

    api = Shodan(SHODAN_API_KEY)
    fail = 0
    # Shodan sometimes fails with no reason, sleeping when it happens and it prevents rate limitation
    try:
        # Search Shodan
        results = api.search("geo:" + lat + "," + lon + ",15 " + query)
    except:
        fail = 1
        print('fail1')

    if fail == 1:
        try:
            results = api.search("geo:" + lat + "," + lon + ",15 " + query)
        except Exception as e:
            print(e)

    try:  # Show the results
        total = len(results['matches'])
        for counter, result in enumerate(results['matches']):
            if 'product' in result:
                product = result['product']
            else:
                product = ""
            current_task.update_state(state='PROGRESS',
                                      meta={'current': counter, 'total': total,
                                            'percent': int((float(counter) / total) * 100)})
            device1 = DeviceNearby(device=device, ip=result['ip_str'], product=product, org=result['org'],
                                   port=str(result['port']), lat=str(result['location']['latitude']),
                                   lon=str(result['location']['longitude']))
            device1.save()

        return {'current': total, 'total': total, 'percent': 100}
    except Exception as e:
        print(e)


@shared_task(bind=True)
def shodan_search(self, fk, country=None, coordinates=None, ics=None, healthcare=None, coordinates_search=None,
                  all_results=False):
    progress_recorder = ProgressRecorder(self)
    result = 0
    if country:
        total = len(ics)
        for c, i in enumerate(ics):
            if healthcare:
                if i in healthcare_queries:
                    print(i)
                    try:
                        result += c
                        shodan_search_worker(country=country, fk=fk, query=healthcare_queries[i], search_type=i,
                                             category="healthcare",
                                             all_results=all_results)
                        progress_recorder.set_progress(c + 1, total=total)
                    except:
                        pass
            else:

                if i in ics_queries:
                    try:
                        result += c
                        shodan_search_worker(country=country, fk=fk, query=ics_queries[i], search_type=i,
                                             category="ics",
                                             all_results=all_results)
                        progress_recorder.set_progress(c + 1, total=total)
                    except:
                        pass

    if coordinates:
        total = len(coordinates_search)
        print(total)
        for c, i in enumerate(coordinates_search):
            # print(coordinates_search[i])
            if i in coordinates_queries:
                try:
                    result += c
                    shodan_search_worker(fk=fk, query=coordinates_queries[i], search_type=i, category="coordinates",
                                         coordinates=coordinates, all_results=all_results)
                    progress_recorder.set_progress(c + 1, total=total)
                except:
                    pass
    return result


def check_credits():
    keys_list = []
    try:
        SHODAN_API_KEY = keys['keys']['shodan']

        api = Shodan(SHODAN_API_KEY)
        a = api.info()
        keys_list.append(a['query_credits'])
    except Exception as e:
        print(e)

    try:
        be_key = keys['keys']['binaryedge']
        headers = {"X-Key": be_key}
        req = requests.get("https://api.binaryedge.io/v2/user/subscription", headers=headers)
        req_json = json.loads(req.content)
        keys_list.append(req_json['requests_left'])
    except Exception as e:
        print(e)

    return keys_list


def shodan_search_worker(fk, query, search_type, category, country=None, coordinates=None, all_results=False):
    results = True
    page = 1
    SHODAN_API_KEY = keys['keys']['shodan']
    pages = 0
    screenshot = ""
    print(query)

    while results:
        if pages == page:
            results = False
            break

        # Shodan sometimes fails with no reason, sleeping when it happens and it prevents rate limitation
        search = Search.objects.get(id=fk)
        api = Shodan(SHODAN_API_KEY)
        fail = 0

        try:
            time.sleep(5)
            if coordinates:
                results = api.search("geo:" + coordinates + ",20 " + query, page)
            if country:
                results = api.search("country:" + country + " " + query, page)
        except:
            fail = 1
            print('fail1, sleeping...')

        if fail == 1:
            try:
                time.sleep(10)
                if coordinates:
                    results = api.search("geo:" + coordinates + ",20 " + query, page)
                if country:
                    results = api.search("country:" + country + " " + query, page)
            except Exception as e:
                results = False
                print(e)
        try:
            total = results['total']

            if total == 0:
                print("no results")
                break
        except Exception as e:
            print(e)
            break

        pages = math.ceil(total / 100) + 1
        print(pages)

        for counter, result in enumerate(results['matches']):
            lat = str(result['location']['latitude'])
            lon = str(result['location']['longitude'])
            city = ""
            indicator = []
            # print(counter)
            # time.sleep(20)

            try:
                product = result['product']
            except:
                product = ""

            if 'vulns' in result:
                vulns = [*result['vulns']]
            else:
                vulns = ""

            if result['location']['city'] != None:
                city = result['location']['city']

            hostnames = ""
            try:
                if 'hostnames' in result:
                    hostnames = result['hostnames'][0]
            except:
                pass

            try:
                if 'SAILOR' in result['http']['title']:
                    html = result['http']['html']
                    soup = BeautifulSoup(html)
                    for gps in soup.find_all("span", {"id": "gnss_position"}):
                        coordinates = gps.contents[0]
                        space = coordinates.split(' ')
                        if "W" in space:
                            lon = "-" + space[2][:-1]
                        else:
                            lon = space[2][:-1]
                        lat = space[0][:-1]
            except Exception as e:
                pass

            if 'opts' in result:
                try:
                    screenshot = result['opts']['screenshot']['data']

                    with open("app_kamerka/static/images/screens/" + result['ip_str'] + ".jpg", "wb") as fh:
                        fh.write(base64.b64decode(screenshot))
                        fh.close()
                        for i in result['opts']['screenshot']['labels']:
                            indicator.append(i)
                except Exception as e:
                    pass

            if query == "Niagara Web Server":
                try:
                    soup = BeautifulSoup(result['http']['html'], features="html.parser")
                    nws = soup.find("div", {"class": "top"})
                    indicator.append(nws.contents[0])
                except:
                    pass

            # get indicator from niagara fox
            if result['port'] == 1911 or result['port'] == 4911:
                try:
                    fox_data_splitted = result['data'].split("\n")
                    for i in fox_data_splitted:
                        if "station.name" in i:
                            splitted = i.split(":")
                            indicator.append(splitted[1])
                except:
                    pass

            # get indicator from tank
            if result['port'] == 10001:
                try:
                    tank_info = result['data'].split("\r\n\r\n")
                    indicator.append(tank_info[1])
                except:
                    pass

            if result['port'] == 2000:
                try:
                    ta_data = result['data'].split("\\n")
                    indicator.append(ta_data[1][:-3])
                except Exception as e:
                    pass

            if result['port'] == 502:
                try:
                    sch_el = result['data'].split('\n')
                    if sch_el[4].startswith("-- Project"):
                        indicator.append(sch_el[4].split(": ")[1])
                except:
                    pass

            if "GPGGA" in result['data']:
                try:
                    splitted_data = result['data'].split('\n')
                    for i in splitted_data:
                        if "GPGGA" in i:
                            msg = pynmea2.parse(i)
                            lat = msg.latitude
                            lon = msg.longitude
                            break
                except Exception as e:
                    print(e)

            if result['port'] == 102:
                try:
                    s7_data = result['data'].split("\n")
                    for i in s7_data:
                        if i.startswith("Plant"):
                            indicator.append(i.split(":")[1])
                        if i.startswith("PLC"):
                            indicator.append(i.split(":")[1])
                        if i.startswith("Module name"):
                            indicator.append(i.split(":")[1])
                except:
                    pass
            # get indicator from bacnet
            if result['port'] == 47808:
                try:
                    bacnet_data_splitted = result['data'].split("\n")
                    for i in bacnet_data_splitted:
                        if "Description" in i:
                            splitted1 = i.split(":")
                            indicator.append(splitted1[1])
                        if "Object Name" in i:
                            splitted2 = i.split(":")
                            indicator.append(splitted2[1])

                        if "Location" in i:
                            splitted3 = i.split(":")
                            indicator.append(splitted3[1])
                except:
                    pass

            device = Device(search=search, ip=result['ip_str'], product=product, org=result['org'],
                            data=result['data'], port=str(result['port']), type=search_type, city=city,
                            lat=lat, lon=lon,
                            country_code=result['location']['country_code'], query=search_type, category=category,
                            vulns=vulns, indicator=indicator, hostnames=hostnames, screenshot=screenshot)
            device.save()

        page = page + 1
        if not all_results:
            results = False

def nmap_host_worker(host_arg,max_reader, search):
    ports_list = []
    hostname = host_arg.hostnames[0]

    a = max_reader.get(host_arg.address)
    print(a['location']['latitude'])
    print(a['location']['longitude'])
    for ports in host_arg.services:
        if ports.state == 'open':
            ports_list.append(ports.port)
        else:
            ports_list.append("None")

    ports_string = ', '.join(str(e) for e in ports_list)
    print(ports_string)
    device = Device(search=search, ip=host_arg.address, product="", org="",
                    data="", port=ports_string, type="NMAP", city="NMAP",
                    lat=a['location']['latitude'], lon=a['location']['longitude'],
                    country_code=a['country']['iso_code'], query="NMAP SCAN", category="NMAP",
                    vulns="", indicator="", hostnames=hostname, screenshot="")
    device.save()

def validate_nmap(file):
    NmapParser.parse_fromfile(os.getcwd() + file)

def validate_maxmind():
    maxminddb.open_database('GeoLite2-City.mmdb')

@shared_task(bind=True)
def nmap_scan(self,file, fk):
    progress_recorder = ProgressRecorder(self)
    result = 0
    print(os.getcwd() + file)
    search = Search.objects.get(id=fk)
    max_reader = maxminddb.open_database('GeoLite2-City.mmdb')
    nmap_report = NmapParser.parse_fromfile(os.getcwd() + file)
    total = len(nmap_report.hosts)
    for c, i in enumerate(nmap_report.hosts):
        result += c
        nmap_host_worker(host_arg=i, max_reader=max_reader, search=search)
        progress_recorder.set_progress(c + 1, total=total)
    return result

@shared_task(bind=False)
def twitter_nearby_task(id, lat, lon):
    # Twitter
    TWITTER_ACCESS_TOKEN = keys['keys']['twitter_access_token']
    TWITTER_ACCESS_TOKEN_SECRET = keys['keys']['twitter_access_token_secret']
    TWITTER_CONSUMER_KEY = keys['keys']['twitter_consumer_key']
    TWITTER_CONSUMER_SECRET = keys['keys']['twitter_consumer_secret']

    twitter = Twitter(auth=OAuth(TWITTER_ACCESS_TOKEN,
                                 TWITTER_ACCESS_TOKEN_SECRET,
                                 TWITTER_CONSUMER_KEY,
                                 TWITTER_CONSUMER_SECRET))

    device1 = Device.objects.get(id=id)
    num_pages = 20
    pages = 0
    last_id = None
    while pages < num_pages:
        try:
            query = twitter.search.tweets(q="", geocode=lat + "," + lon, count=100,
                                          include_entities=True, max_id=last_id, result_type='mixed')
            pages += 1
            current_task.update_state(state='PROGRESS',
                                      meta={'current': pages, 'total': num_pages,
                                            'percent': int((float(pages) / num_pages) * 100)})
            print(str(pages) + " page")
            for counter, result in enumerate(query["statuses"]):
                if 'coordinates' in result:
                    if result['coordinates'] != None:
                        tw = TwitterNearby(device=device1, lat=str(result['coordinates']['coordinates'][0]),
                                           lon=str(result['coordinates']['coordinates'][1]),
                                           tweet=result['text'].encode('ascii', 'ignore')
                                           )
                        tw.save()

        except TwitterHTTPError as e:
            print(e.args)

    return {'current': num_pages, 'total': num_pages, 'percent': 100}


def paste_login(username, password, key):
    login_url = "https://pastebin.com/api/api_login.php"
    login_payload = {"api_dev_key": key, "api_user_name": username, "api_user_password": password}

    login = requests.post(login_url, data=login_payload)
    user_key = login.text
    return user_key


def retrieve_pastes(key, user_key):
    url = "http://pastebin.com/api/api_post.php"
    paste_dict = {}

    values_list = {'api_option': 'list',
                   'api_dev_key': key,
                   'api_user_key': user_key}

    data = urllib.parse.urlencode(values_list)
    data = data.encode('utf-8')  # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()

    key_v = ""
    title = ""

    root = et.fromstring("<root>" + str(the_page) + "</root>")
    for paste_root in root:
        for paste_element in paste_root:
            key = paste_element.tag.split("_", 1)[-1]
            if key == "key":
                key_v = paste_element.text
            if key == "title":
                title = paste_element.text

        paste_dict[title] = key_v
    return paste_dict


def delete_paste(key, user_key, paste_code):
    url = "http://pastebin.com/api/api_post.php"

    values_list = {'api_option': 'delete',
                   'api_dev_key': key,
                   'api_user_key': user_key,
                   "api_paste_key": paste_code}

    data = urllib.parse.urlencode(values_list)
    data = data.encode('utf-8')  # data should be bytes
    req = urllib.request.Request(url, data)
    urllib.request.urlopen(req)


def create_paste(key, user_key, filename, text):
    url = "http://pastebin.com/api/api_post.php"

    values = {'api_option': 'paste',
              'api_dev_key': key,
              'api_paste_code': text,
              'api_paste_private': '2',
              'api_paste_name': filename,
              'api_user_key': user_key}

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')  # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()


@shared_task(bind=False)
def send_to_field_agent_task(id, notes):
    cve = ""
    indicator = ""

    af = Device.objects.get(id=id)
    ports = af.port
    try:
        af_details = ShodanScan.objects.get(device_id=id)
        ports = af_details.ports[1:][:-1]
        if af_details.vulns:
            cve = af_details.vulns[1:][:-1]
        if af.indicator:
            indicator = af.indicator[2:][:-2]
    except:
        print("Not scanned")
        pass

    user_key = paste_login(keys['keys']['pastebin_user'], keys['keys']['pastebin_password'],
                           keys['keys']['pastebin_dev_key'])

    pastes = retrieve_pastes(keys['keys']['pastebin_dev_key'], user_key=user_key)

    ip = af.ip
    lat = af.lat
    lon = af.lon
    org = af.org
    type = af.type

    notes = af.notes

    merge_string = "ꓘ;" + lat + ";" + lon + ";" + ip + ";" + ports + ";" + org + ";" + type + ";" + cve + ";" + indicator + ";" + notes

    print("\\xea\\x93\\x98amerka_" + af.ip)
    if "\\xea\\x93\\x98amerka_" + af.ip in pastes.keys():
        delete_paste(keys['keys']['pastebin_dev_key'], user_key, pastes["\\xea\\x93\\x98amerka_" + af.ip])
        create_paste(keys['keys']['pastebin_dev_key'], user_key, "ꓘamerka_" + af.ip, merge_string)
    else:
        create_paste(keys['keys']['pastebin_dev_key'], user_key, "ꓘamerka_" + af.ip, merge_string)


@shared_task(bind=False)
def flickr(id, lat, lon):
    FLICKR_API_KEY = keys['keys']['flickr_api_key']
    FLICKR_SECRET_API_KEY = keys['keys']['flickr_api_key']
    device1 = Device.objects.get(id=id)

    flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_SECRET_API_KEY)
    try:
        photo_list = flickr.photos.search(api_key=FLICKR_API_KEY, lat=lat, lon=lon, accuracy=16, format='parsed-json',
                                          per_page=100, extras='url_l,geo', has_geo=1, sort='newest')
    except Exception as e:
        print(e.args)

    total = 100

    for counter, photo in enumerate(photo_list['photos']['photo']):
        if 'url_l' in photo:
            flickr_db = FlickrNearby(device=device1, lat=str(photo['latitude']),
                                     lon=str(photo['longitude']), title=photo['title'], url=photo['url_l'])
            flickr_db.save()
            print(counter)
            current_task.update_state(state='PROGRESS',
                                      meta={'current': counter, 'total': total,
                                            'percent': int((float(counter) / total) * 100)})

    return {'current': total, 'total': total, 'percent': 100}


@shared_task(bind=False)
def shodan_scan_task(id):
    SHODAN_API_KEY = keys['keys']['shodan']
    device = Device.objects.get(id=id)
    api = Shodan(SHODAN_API_KEY)
    product = []
    tags = []
    vulns = []
    try:
        # Search Shodan
        results = api.host(device.ip)
        # Show the results
        total = len(results['ports'])
        print(total)
        for counter, i in enumerate(results['data']):

            if 'product' in i:
                product.append(i['product'])

            if 'tags' in i:
                for j in i['tags']:
                    tags.append(j)

            current_task.update_state(state='PROGRESS',
                                      meta={'current': counter, 'total': total,

                                            'percent': int((float(counter) / total) * 100)})
        if 'vulns' in results:
            vulns = results['vulns']

        ports = results['ports']
        device1 = ShodanScan(device=device, products=product,
                             ports=ports, tags=tags, vulns=vulns)
        device1.save()
        print(results['ports'])

        return {'current': total, 'total': total, 'percent': 100}

    except Exception as e:
        print(e.args)


@shared_task(bind=False)
def binary_edge_scan(id):
    key = keys['keys']['binaryedge']
    device1 = Device.objects.get(id=id)
    be = BinaryEdge(key)
    results = be.host_score(device1.ip)
    normalized_ip_score = results['normalized_ip_score']

    cve = {}

    if 'cve' in results['results_detailed']:
        for cc in results['results_detailed']['cve']['result']:
            if isinstance(cc['cve'], list):
                for i in cc['cve']:
                    cve[i['cpe']] = i['cve_list']
            if isinstance(cc['cve'], dict):
                if 'cpe' in cc['cve']:
                    cve[cc['cve']['cpe'][0]] = cc['cve']['cve_list']

    device2 = BinaryEdgeScore(device=device1, grades=results['ip_score_detailed'], cve=cve, score=normalized_ip_score)
    device2.save()


@shared_task(bind=False)
def whoisxml(id):
    api_key = keys['keys']['whoisxmlapi']
    device1 = Device.objects.get(id=id)

    end = "https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=" + api_key + "&domainName=" + device1.ip + "&outputFormat=json"

    req = requests.get(end)

    req_json = json.loads(req.content)

    netrange = ""
    admin_org = ""
    admin_email = ""
    admin_phone = ""
    city = ""
    email = ""
    street = ""
    name = ""
    org = ""

    if 'administrativeContact' in req_json['WhoisRecord']['registryData']:
        admin_email = req_json['WhoisRecord']['registryData']['administrativeContact']['email'],
        admin_phone = req_json['WhoisRecord']['registryData']['administrativeContact']['telephone'],
        admin_org = req_json['WhoisRecord']['registryData']['administrativeContact']['organization']

    if 'registrant' in req_json['WhoisRecord']['registryData']:
        if "name" in req_json['WhoisRecord']['registryData']['registrant']:
            name = req_json['WhoisRecord']['registryData']['registrant']['name']
        if "organization" in req_json['WhoisRecord']['registryData']['registrant']:
            org = req_json['WhoisRecord']['registryData']['registrant']['organization']
        if "street1" in req_json['WhoisRecord']['registryData']['registrant']:
            street = req_json['WhoisRecord']['registryData']['registrant']['street1']

        if req_json['WhoisRecord']['registryData']['customField1Name'] == "netRange":
            netrange = req_json['WhoisRecord']['registryData']['customField1Value']
        if req_json['WhoisRecord']['registryData']['customField2Name'] == "netRange":
            netrange = req_json['WhoisRecord']['registryData']['customField2Value']

        if 'city' in req_json['WhoisRecord']['registryData']['registrant']:
            city = req_json['WhoisRecord']['registryData']['registrant']['city']

        if 'email' in req_json['WhoisRecord']['registryData']['registrant']:
            email = req_json['WhoisRecord']['registryData']['registrant']['email']

        wh = Whois(device=device1, org=org,
                   street=street,
                   city=city,
                   admin_org=admin_org,
                   admin_email=admin_email,
                   admin_phone=admin_phone, netrange=netrange, name=name, email=email)

        wh.save()


    elif 'subRecords' in req_json['WhoisRecord']:
        try:
            if "name" in req_json['WhoisRecord']['subRecords'][0]['registrant']:
                name = req_json['WhoisRecord']['subRecords'][0]['registrant']['name']
                if "street1" in req_json['WhoisRecord']['subRecords'][0]['registrant']:
                    street = req_json['WhoisRecord']['subRecords'][0]['registrant']['street1']
        except:
            pass

        try:
            if req_json['WhoisRecord']['subRecords'][0]['customField1Name'] == "netRange":
                netrange = req_json['WhoisRecord']['subRecords'][0]['customField1Value']
            if req_json['WhoisRecord']['subRecords'][0]['customField2Name'] == "netRange":
                netrange = req_json['WhoisRecord']['subRecords'][0]['customField2Value']
        except:
            pass

        try:
            org = req_json['WhoisRecord']['subRecords'][0]['registrant']['organization']
            if 'city' in req_json['WhoisRecord']['subRecords'][0]['registrant']:
                city = req_json['WhoisRecord']['subRecords'][0]['registrant']['city']

            if 'email' in req_json['WhoisRecord']['subRecords'][0]['registrant']:
                email = req_json['WhoisRecord']['subRecords'][0]['registrant']['email']
        except:
            pass

        wh = Whois(device=device1, org=org,
                   street=street,
                   city=city,
                   admin_org=admin_org,
                   admin_email=admin_email,
                   admin_phone=admin_phone, netrange=netrange, name=name, email=email)

        wh.save()
