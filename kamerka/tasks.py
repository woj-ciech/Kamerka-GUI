import json
import math

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

from app_kamerka.models import Device, DeviceNearby, Search, TwitterNearby, FlickrNearby, ShodanScan, BinaryEdgeScore, \
    Whois

ics_queries = {"niagara": "port:1911,4911 product:Niagara",
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
               "nordex": "Jetty 3.1.8 (Windows 2000 5.0 x86) \"200 OK\" ",
               "sailor":"http.favicon.hash:-1222972060",
               'nmea':"$GPGGA"}

coordinates_queries = {"webcam": "device:webcam",
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
                       'zworld': "Z-World Rabbit 200 OK",
                       "nordex": "Jetty 3.1.8 (Windows 2000 5.0 x86) \"200 OK\" "
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
def shodan_search(self, fk, country=None, coordinates=None, ics=None, coordinates_search=None, all_results=False):
    progress_recorder = ProgressRecorder(self)
    result = 0
    if country:
        total = len(ics)
        for c, i in enumerate(ics):
            print(ics_queries[i])
            if i in ics_queries:
                result += c
                shodan_search_worker(country=country, fk=fk, query=ics_queries[i], search_type=i, category="ics",
                                     all_results=all_results)
                progress_recorder.set_progress(c + 1, total=total)
    if coordinates:
        total = len(coordinates_search)
        print(total)
        for c, i in enumerate(coordinates_search):
            # print(coordinates_search[i])
            if i in coordinates_queries:
                result += c
                shodan_search_worker(fk=fk, query=coordinates_queries[i], search_type=i, category="coordinates",
                                     coordinates=coordinates, all_results=all_results)
                progress_recorder.set_progress(c + 1, total=total)

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
        print(query)

        for counter, result in enumerate(results['matches']):
            lat = str(result['location']['latitude'])
            lon = str(result['location']['longitude'])
            city = ""
            indicator = []
            print(counter)
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

                    with open("app_kamerka/static/images/screens/"+result['ip_str']+".jpg", "wb") as fh:
                        fh.write(base64.b64decode(screenshot))
                        fh.close()
                        for i in result['opts']['screenshot']['labels']:
                            indicator.append(i)
                except Exception as e:
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
            elif result['port'] == 10001:
                try:
                    tank_info = result['data'].split("\r\n\r\n")
                    indicator.append(tank_info[1])
                except:
                    pass

            if "GPGGA" in result['data']:
                try:
                    print('in')
                    splitted_data = result['data'].split('\n')
                    for i in splitted_data:
                        if "GPGGA" in i:
                            msg = pynmea2.parse(i)
                            lat = msg.latitude
                            lon = msg.longitude
                            break
                except Exception as e:
                    print(e)


            # get indicator from bacnet
            elif result['port'] == 47808:
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
            else:
                indicator = ""

            device = Device(search=search, ip=result['ip_str'], product=product, org=result['org'],
                            data=result['data'], port=str(result['port']), type=search_type, city=city,
                            lat=lat, lon=lon,
                            country_code=result['location']['country_code'], query=search_type, category=category,
                            vulns=vulns, indicator=indicator, hostnames=hostnames, screenshot=screenshot)
            device.save()


        page = page + 1
        if not all_results:
            results = False


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
    try:
        # Search Shodan
        results = api.host(device.ip)
        # Show the results
        total = len(results['ports'])
        for counter, i in enumerate(results['data']):

            product = ''
            tags = ""

            if 'product' in i:
                product = i['product']

            if 'tags' in i:
                tags = i['tags']

            print(counter)
            device1 = ShodanScan(device=device, products=product,
                                 ports=str(i['port']), module=i['_shodan']['module'], tags=tags)
            device1.save()
            current_task.update_state(state='PROGRESS',
                                      meta={'current': counter, 'total': total,
                                            'percent': int((float(counter) / total) * 100)})
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
