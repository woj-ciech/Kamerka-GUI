import ast
import json
from collections import Counter
import requests
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
import pycountry
from celery.result import AsyncResult
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app_kamerka import forms
from app_kamerka.models import Search, Device, DeviceNearby, FlickrNearby, ShodanScan, BinaryEdgeScore, Whois, \
    TwitterNearby, Bosch
from kamerka.tasks import shodan_search, devices_nearby, twitter_nearby_task, flickr, shodan_scan_task, \
    binary_edge_scan, whoisxml, check_credits, send_to_field_agent_task, nmap_scan, validate_nmap, validate_maxmind, scan, \
    exploit


# Create your views here.

passwds = {"bosch_security":"""The Bosch Video Recorder 630/650 Series is an 8/16 
          channel digital recorder that uses the latest H.264 
          compression technology. With the supplied PC
          software and built-in web server, the 630/650 Series is
          a fully integrated, stand-alone video management
          solution that's ready to go, straight out of the box.
          Available with a variety of storage capacities, the
          630/650 Series features a highly reliable embedded
          design that minimizes maintenance and reduces
          operational costs. The recorder is also available with a
          built-in DVD writer <br>
          https://www.exploit-db.com/exploits/34956 """,
           "niagara":"Tridium is the developer of Niagara Framework® — a comprehensive software platform for the development and deployment of connected products and device-to-enterprise applications. Niagara provides the critical device connectivity, cyber security, control, data management, device management and user presentation capabilities needed to extract value and insight from real-time operational data <br> Default credentials: <br>tridium:niagara",
           "siemens":"S7 (S7 Communication) is a Siemens proprietary protocol that runs between programmable logic controllers (PLCs) of the Siemens S7 family. <br>Default credentials: <br> Hardcoded password: Basisk:Basisk <br> admin:blank",
           "bacnet":"BACnet is a communications protocol for building automation and control networks. It was designed to allow communication of building automation and control systems for applications such as heating, air-conditioning, lighting, and fire detection systems.",
           "modbus":"Modbus is a popular protocol for industrial control systems (ICS). It provides easy, raw access to the control system without requiring any authentication.",
           "dnp3":"DNP3 (Distributed Network Protocol) is a set of communications protocols used between components in process automation systems. Its main use is in utilities such as electric and water companies.",
           "plantivosr":"PlantVisor Enhanced is monitoring and telemaintenance software for refrigeration and air-conditioning systems controlled by CAREL instruments. PlantVisor, thanks to the embedded Web Server, can be used on a series of PCs connected to a TCP/IP network. In this way, the information can be shared by a number of users at the same time. <br> Default credentials: <br> admin:admin",
           "iologik":"The ioLogik E1200 Series supports the most often-used protocols for retrieving I/O data, making it capable of handling a wide variety of applications. Most IT engineers use SNMP or RESTful API protocols, but OT engineers are more familiar with OT-based protocols, such as Modbus and EtherNet/IP. <br>Default credentials: <br> administrator:blank",
           "akcp":"The AKCP sensorProbe+ series of base units are our flagship Remote Environmental Sensor Monitoring Device. Our sensor monitoring systems are deployed in a wide variety of industries including Data Center Environmental Monitoring, Warehouse Temperature Monitoring, Cold Storage Temperature Monitoring, Fuel / Generator Monitoring, and other Remote Site Monitoring applications.<br>Default credentials: <br> administrator:public <br> admin:public",
           "vtscada":"https://www.vtscada.com/wp-content/uploads/2016/09/VTScada11-2-AdminGuide.pdf",
           "sailor":"<br>Default credentials: <br> admin:1234 <br> https://www.livewire-connections.com/sites/default/files/files/documents/Sailor%20900%20Ka%20Installation%20Manual.pdf",
           "digi":"Digi TransPort WR21 is a full-featured cellular router offering the flexibility to scale from basic connectivity applications to enterprise class routing and security solutions. With its high-performance architecture, Digi TransPort WR21 provides primary and backup WWAN connectivity over 3G/4G/LTE. The platform includes software selectable multi-carrier and regional LTE variants. <br>Default credentials:<br>username:password",
           "ilon":"The i.LON® SmartServer is a low-cost, high-performance controller, network manager, router, remote network interface, and Web server that you can use to connect LONWORKS®, Modbus, and M-Bus devices to corporate IP networks or the Internet.  <br>Default credentials: <br> for ftp and lns servers:, ilon:ilon <br> ",
           "eig":"<br>Default credentials: <br> anonymous:anonymous <br> eignet:inp100",
            "mitsubishi":"<br>Default credentials: <br> MELSEC:MELSEC <br> QNUDECPU:QNUDECPU <br> MELSEC-Q Series use a proprietary network protocol for communication. The devices are used by equipment and manufacturing facilities to provide high-speed, large volume data processing and machine control.",
           "moxahttp": "NPort® 5100 device servers are designed to make serial devices network-ready in an instant. The small size of the servers makes them ideal for connecting devices such as card readers and payment terminals to an IP-based Ethernet LAN. Use the NPort 5100 device servers to give your PC software direct access to serial devices from anywhere on the network. <br>Default credentials: <br> admmin:moxa",
           "omron":"FINS, Factory Interface Network Service, is a network protocol used by Omron PLCs, over different physical networks like Ethernet, Controller Link, DeviceNet and RS-232C. <br>Default credentials: <br> for http: ETHERNET, for ftp: CONFIDENTIAL <br> default:default",
            "power_logic":"https://www.se.com/ww/en/product-range/62252-powerlogic-pm8000-series/?selected-node-id=12146165208#tabs-top <br>Default credentials: <br> 0000 <br> 0 <br> Administrator:Gateway <br> Administrator:admin, User 1:master, User 2:engineer, User 3:operator",
            "scalance":"SCALANCE network components form the basis of communication networks in manufacturing and process automation. Make your industrial networks fit for the future! SCALANCE products have been specially designed for use in industrial applications. As a result, they fulfill all requirements for ultra-efficient industrial networks and bus systems. Whether switching, routing, security applications, remote access or Industrial Wireless LAN – SCALANCE is the solution!  <br>Default credentials: <br> admin:admin (HTTP), user:user (HTTP), siemens:siemens (FTP)",
            "stulz_klimatechnik":"he WIB (Web Interface Board) is an interface between STULZ air conditioning units and the intranet or inter-net via an ethernet connection. This connection allows monitoring and control of  A/C units. On the operators’s side the appropriate hardware (PC or server) and the appropriate software (SNMP client and/or web browser) are necessary. <br>Default credentials: <br> Administrator, highest authorization:, ganymed, Medium authorization:, kallisto, Lowest authorization:, europa ",
           "wago":"<br>Default credentials: <br> admin:wago, user:user, guest:guest <br> http, ftp:, user:user00 , administrator:, su:ko2003wa <br> root:wago , admin:wago, user:user , guest:guest ",
           "axis":"<br>Default credentials: <br> root:pass",
           "intellislot":"Provides Web access, environmental sensor data, and third-party customer protocols for Vertiv™ equipment. The cards employ Ethernet and RS-485 networks to monitor and manage a wide range of operating parameters, alarms and notifications. Provides a communication interface to Trellis™, LIFE™ Services, Liebert® Nform, and third-party building and network management applications. <br>Default credentials: <br> Liebert:Liebert, User:User",
           "iqinvision":"<br>Default credentials: <br> root:system",
           "lantronix":"Lantronix EDS-MD is specifically designed for the medical industry, allowing for remote access and management of electronic and medical devices. <br>Default credentials: <br> admin:PASS ",
           "loytec":"https://www.loytec.com/support/download/lvis-3me7-g2 <br>Default credentials: <br> admin:loytec4u",
           "videoiq" : "VideoIQ develops intelligent video surveillance cameras using edge video IP security cameras paired with video analytics. <br> VideoIQ is vulnerable to remote file disclosure which allows to any unauthenticated user read any file system including file configurations.<br>Default credentials"
                       "<br>supervisor:supervisor <br> https://www.exploit-db.com/exploits/40284",
           "webcamxp":"""webcamXP is the most popular webcam and network camera software for Windows.It allows you to monitor your belongings from any location with access to Internet by turning your computer into a security system.
            Connect remotely by using other computers or your mobile phone. Broadcast live video to your website. Schedule automatic captures or recordings. Trig specific actions using the motion detector. You can easily use those features among others with webcamXP.<br>Default credentials:<br>admin:<blank>""",
           "vivotek":"Default credentials:<br>root:<blank>",
           "mobotix":"https://www.mobotix.com/en/products/outdoor-cameras<br>Default credentials:<br>admin:meinsm",
           "grandstream":"Create and customize a security environment with Grandstream’s range of Full HD IP cameras. Easy to setup, deploy and manage, these cameras offer a proactive security system to keep a user’s facility secured and protected. The GSC3600 series of HD IP cameras feature full HD resolution and include weatherproof casing designed for increased security and facility management in any indoor or outdoor area for wide-angle monitoring of nearby subjects.<br>Default credentials:<br>admin:meinsm<br>https://www.exploit-db.com/exploits/48247",
           "contec":"http://www.contec-touch.com/wireless-smart-home/ <br> https://www.exploit-db.com/exploits/44295",
           "netwave":"https://www.exploit-db.com/exploits/41236",
           "CirCarLife":"CirCarlife Scada represents an integral software solution that focuses on the control and parameterisation of smart electric vehicle charging points and units. It gives centralised control of the whole installation for management and maintenance purposes.<br>https://www.exploit-db.com/exploits/45384",
           "amcrest":"https://www.exploit-db.com/exploits/47188",
           "lutron":"Quantum is a lighting control and energy management system that provides total light management by tying the most complete line of lighting controls, motorized window shades, digital ballasts and LED drivers, and sensors together under one software umbrella. Quantum is ideal for new construction or retrofit applications and can easily scale from a single area to a building, or to a campus with many buildings.<br>https://www.exploit-db.com/exploits/44488",
           }

def get_keys():
    try:
        with open('keys.json') as keys:
            keys_json = json.load(keys)

        return keys_json
    except Exception as e:
        print(e)


keys = get_keys()


def search_main(request):
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        coordinates_form = forms.CoordinatesForm(request.POST)
        ics_form = forms.CountryForm(request.POST)
        healthcare_form = forms.CountryHealthcareForm(request.POST)

        if ics_form.is_valid():
            code = ics_form.cleaned_data['country']

            ics_country = request.POST.getlist('ics_country')

            if len(ics_country) == 0:
                form = forms.CountryForm()
                return render(request, 'search_main.html', {'form': form})

            search = Search(country=code, ics=ics_country)
            search.save()
            post = request.POST.getlist('ics_country')

            if ics_form.cleaned_data['all'] == True:
                all_results = True
            else:
                all_results = False

            shodan_search_task = shodan_search.delay(fk=search.id, country=code, ics=post, all_results=all_results)
            request.session['task_id'] = shodan_search_task.task_id

            return HttpResponseRedirect('index')


        elif healthcare_form.is_valid():
            code = healthcare_form.cleaned_data['country_healthcare']

            healthcare_country = request.POST.getlist('healthcare')


            if len(healthcare_country) == 0:

                form = forms.CountryHealthcareForm()
                return render(request, 'search_main.html', {'form': form})

            search = Search(country=code, ics=healthcare_country)
            search.save()
            post = request.POST.getlist('healthcare')

            if healthcare_form.cleaned_data['all'] == True:
                all_results = True
            else:
                all_results = False

            shodan_search_task = shodan_search.delay(fk=search.id, country=code, ics=post, healthcare=True, all_results=all_results)
            request.session['task_id'] = shodan_search_task.task_id

            return HttpResponseRedirect('index')

        elif coordinates_form.is_valid():

            coordinates = coordinates_form.cleaned_data['coordinates']
            if len(coordinates) == 0:
                form = forms.CountryForm()
                return render(request, 'search_main.html', {'form': form})

            search = Search(coordinates=coordinates_form.cleaned_data['coordinates'],
                            coordinates_search=request.POST.getlist('coordinates_search'))

            search.save()
            shodan_search_task = shodan_search.delay(fk=search.id, coordinates=coordinates,
                                     coordinates_search=request.POST.getlist('coordinates_search'))

            request.session['task_id'] = shodan_search_task.task_id

            return HttpResponseRedirect('index')

        try:
            myfile = request.FILES['myfile']
        except:
            form = forms.CountryForm()
            return render(request, 'search_main.html', {'form': form})

        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            try:
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                print(uploaded_file_url)
                validate_nmap(uploaded_file_url)
                validate_maxmind()
                search = Search(country="NMAP Scan", ics=myfile.name,nmap=True)
                search.save()
                nmap_task = nmap_scan.delay(uploaded_file_url ,fk=search.id)

                request.session['task_id'] = nmap_task.task_id
                print('session')
            except Exception as e:
                print(e)
                return JsonResponse({'message':str(e)}, status=500)

            return HttpResponseRedirect('index')

        else:

            form = forms.CountryForm()
            return render(request, 'search_main.html', {'form': form})

    else:
        form = forms.CountryForm()
        return render(request, 'search_main.html', {'form': form})

def index(request):
    all_devices = Device.objects.all()
    last_5_searches = Search.objects.filter().order_by('-id')[:5]
    ics_len = Device.objects.filter(category="ics")
    coordinates_search_len = Device.objects.filter(category="coordinates")
    healthcare_len = Device.objects.filter(category="healthcare")
    search_all = Search.objects.all()
    task = request.session.get('task_id')
    ports = Device.objects.values('port').annotate(c=Count('port')).order_by('-c')[:7]
    ports_list = list(ports)
    vulns = Device.objects.exclude(vulns__isnull=True).exclude(vulns__exact='')

    vulns_list = []

    for i in vulns:
        vulns_list.append(ast.literal_eval(i.vulns))

    cves = []
    for i in vulns_list:
        for j in i:
            cves.append(j)

    countr_cves = {}
    c = Counter(cves)
    for key, value in c.items():
        countr_cves[key] = value

    sort = sorted(countr_cves.items())[:7]

    countries = {}
    for i in search_all:
        countries[i.country] = "1"

    #make list out of last 5 searches
    for j in last_5_searches:
        try:
            j.country = pycountry.countries.get(alpha_2=j.country).name
            j.ics = ast.literal_eval(j.ics)
        except:
            pass
        try:
            j.coordinates_search = ast.literal_eval(j.coordinates_search)
        except:
            pass

    credits = check_credits()

    context = {'device': all_devices,
               "search": last_5_searches,
               "ics": ics_len,
               "coordinates": coordinates_search_len,
               "healthcare":healthcare_len,
               "ports": ports_list,
               "countries": countries,
               'vulns': sort,
               "task_id": task,
               "search_len": search_all,
               "credits": credits}
    return render(request, 'index.html', context)


def devices(request):
    all_devices = Device.objects.all()

    for i in all_devices:
        try:
            i.indicator = ast.literal_eval(i.indicator)
        except:
            pass

    context = {"devices": all_devices}

    return render(request, "devices.html", context=context)

def map(request):
    all_devices = Device.objects.all()

    google_maps_key = keys['keys']['google_maps']

    context = {"devices": all_devices, 'google_maps_key': google_maps_key}

    return render(request, "map.html", context=context)

def gallery(request):
    all_devices = Device.objects.filter(screenshot__gt='',screenshot__isnull=False)
    context = {"devices": all_devices}

    return render(request, "gallery.html", context=context)


def results(request, id):
    all_devices = Device.objects.filter(search_id=id)
    ports = Device.objects.filter(search_id=id).values('port').annotate(c=Count('port')).order_by('-c')[:7]
    city = Device.objects.filter(search_id=id).values('city').annotate(c=Count('city')).order_by('-c')[:7]
    category = Device.objects.filter(search_id=id).values('type').annotate(c=Count('type')).order_by('-c')
    google_maps_key = keys['keys']['google_maps']


    categories_list = list(category)
    ports_list = list(ports)
    cities_list = list(city)

    for i in categories_list:
        i['label'] = i.pop('type')
        i['value'] = i.pop('c')

    vulns = Device.objects.exclude(vulns__isnull=True).exclude(vulns__exact='')

    cves_list = []

    for i in vulns:
        cves_list.append(ast.literal_eval(i.vulns))
    cves = []
    for i in cves_list:
        for j in i:
            cves.append(j)

    cves_counter = {}
    c = Counter(cves)
    for key, value in c.items():
        cves_counter[key] = value

    sort = sorted(cves_counter.items())[:7]

    for i in all_devices:
        try:
            i.indicator = ast.literal_eval(i.indicator)

        except:
            pass


    context = {'search': all_devices,
               'ports': ports_list,
               "vulns": sort,
               "category": categories_list,
               "city": cities_list,
               'google_maps_key': google_maps_key}

    return render(request, 'results.html', context)


def history(request):
    all_searches = Search.objects.all()

    for i in all_searches:
        try:
            i.coordinates_search = ast.literal_eval(i.coordinates_search)
        except Exception as e:
            print(e)

        try:
            i.ics = ast.literal_eval(i.ics)
        except Exception as e:
            print(e)

    context = {'history': all_searches}
    return render(request, 'history.html', context)


def update_coordinates(request,id, coordinates):
    if request.is_ajax() and request.method == 'GET':
        dev = Device.objects.get(id=id)
        splitted_coord = coordinates.split(",")
        dev.lat = splitted_coord[0]
        dev.lon = splitted_coord[1]
        dev.located = True
        dev.save()
        return HttpResponse(json.dumps({'Status': "OK"}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'Status': "NO OK"}), content_type='application/json')


def device(request, id, device_id, ip):
    all_devices = Device.objects.get(search_id=id, id=device_id)
    nearby = DeviceNearby.objects.filter(device_id=all_devices.id)
    flickr = FlickrNearby.objects.filter(device_id=all_devices.id)
    shodan = ShodanScan.objects.filter(device_id=all_devices.id)
    google_maps_key = keys['keys']['google_maps']

    try:
        all_devices.indicator = ast.literal_eval(all_devices.indicator)
    except:
        pass

    if all_devices.type in passwds.keys():
        info = passwds[all_devices.type]
    else:
        info = ""

    context = {'device': all_devices,
               'nearby': nearby,
               'flickr': flickr,
               "shodan": shodan,
               'google_maps_key': google_maps_key,
               "passwd": info}

    return render(request, 'device.html', context)


def nearby(request, id, query):
    if request.is_ajax() and request.method == 'GET':
        all_devices = Device.objects.filter(id=id)
        device_nearby_task = devices_nearby.delay(lat=all_devices[0].lat, lon=all_devices[0].lon, id=id, query=query)
        return HttpResponse(json.dumps({'task_id': device_nearby_task.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def sources(request):
    return render(request, 'sources.html', {})


def twitter_nearby(request, id):
    if request.is_ajax() and request.method == 'GET':

        tw = TwitterNearby.objects.filter(device_id=id)

        if tw:
            print('already')
            return HttpResponse(json.dumps({'Error': "Already in database"}), content_type='application/json')

        a = Device.objects.filter(id=id)
        tw_task = twitter_nearby_task.delay(lat=a[0].lat, lon=a[0].lon, id=id)
        return HttpResponse(json.dumps({'task_id': tw_task.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def twitter_show(request, id):
    if request.is_ajax() and request.method == 'GET':
        a = TwitterNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)
        if not response_data:
            return HttpResponse(json.dumps({'Error': "No records"}), content_type='application/json')
        else:
            return HttpResponse(response_data, content_type="application/json")


def flickr_nearby(request, id):
    if request.is_ajax() and request.method == 'GET':

        fl = FlickrNearby.objects.filter(device_id=id)

        if fl:
            print('already')
            return HttpResponse(json.dumps({'Error': "Already in database"}), content_type='application/json')

        a = Device.objects.get(id=id)

        flickr_task = flickr.delay(lat=a.lat, lon=a.lon, id=id)
        return HttpResponse(json.dumps({'task_id': flickr_task.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def shodan_scan(request, id):
    if request.is_ajax() and request.method == 'GET':

        shodan_scan2 = ShodanScan.objects.filter(device_id=id)

        if shodan_scan2:
            print('already')
            return HttpResponse(json.dumps({'Error': "Already in database"}), content_type='application/json')

        shodan_scan_task2 = shodan_scan_task.delay(id=id)
        return HttpResponse(json.dumps({'task_id': shodan_scan_task2.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def get_task_info(request):
    task_id = request.GET.get('task_id', None)
    try:
        if task_id is not None:
            task = AsyncResult(task_id)
            data = {
                'state': task.state,
                'result': task.result,
            }
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponse('No job id given.')
    except Exception as e:
        print(e)


def get_shodan_scan_results(request, id):
    if request.is_ajax() and request.method == 'GET':
        shodan_scan2 = ShodanScan.objects.filter(device_id=id)

        print(shodan_scan2)

        # shodan_scan2[0].ports = shodan_scan2[0].ports[:1][:-1]
        # shodan_scan2[0].tags = shodan_scan2[0].tags[:1][:-1]
        # shodan_scan2[0].vulns = shodan_scan2[0].vulns[:1][:-1]
        # shodan_scan2[0].products = shodan_scan2[0].products[:1][:-1]

        print(shodan_scan2[0].ports)

        response_data = serializers.serialize('json', shodan_scan2)

        return HttpResponse(response_data, content_type="application/json")


def get_nearby_devices(request, id):
    if request.is_ajax() and request.method == 'GET':
        nearby_devices = DeviceNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', nearby_devices)

        return HttpResponse(response_data, content_type="application/json")

def scan_dev(request, id):
    if request.is_ajax() and request.method == 'GET':
        res = scan(id)
        if res:
            return HttpResponse(json.dumps(res), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'Error': "Connection Error"}), content_type='application/json')

def exploit_dev(request, id):
    if request.is_ajax() and request.method == 'GET':
        res = exploit(id)
        if res:
            return HttpResponse(json.dumps(res), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'Error': "Connection Error"}), content_type='application/json')

def get_flickr_results(request, id):
    if request.is_ajax() and request.method == 'GET':
        nearby_flickr = FlickrNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', nearby_flickr)

        return HttpResponse(response_data, content_type="application/json")


def get_flickr_coordinates(request, id):
    if request.is_ajax() and request.method == 'GET':
        nearby_flickr = FlickrNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', nearby_flickr)

        return HttpResponse(response_data, content_type="application/json")


def get_nearby_devices_coordinates(request, id):
    if request.is_ajax() and request.method == 'GET':
        nearby_devices = DeviceNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', nearby_devices)

        return HttpResponse(response_data, content_type="application/json")

def send_to_field_agent(request, id, notes):
    if request.is_ajax() and request.method == 'GET':
        print(id)

        host = Device.objects.get(id=id)
        host.notes = notes
        host.save()

        af_task = send_to_field_agent_task.delay(id, notes)

        return HttpResponse(json.dumps({'Status': "OK"}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def get_binaryedge_score(request, id):
    if request.is_ajax() and request.method == 'GET':

        be = BinaryEdgeScore.objects.filter(device_id=id)

        if be:
            print('already')
            return HttpResponse(json.dumps({'Error': "Already in database"}), content_type='application/json')

        be_task = binary_edge_scan.delay(id=id)

        return HttpResponse(json.dumps({'task_id': be_task.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def get_binaryedge_score_results(request, id):
    if request.is_ajax() and request.method == 'GET':
        be = BinaryEdgeScore.objects.filter(device_id=id)

        response_data = serializers.serialize('json', be)

        return HttpResponse(response_data, content_type="application/json")


def whois(request, id):
    if request.is_ajax() and request.method == 'GET':

        whoiss = Whois.objects.filter(device_id=id)

        if whoiss:
            print('already')
            return HttpResponse(json.dumps({'Error': "Already in database"}), content_type='application/json')

        wh_task = whoisxml.delay(id=id)

        return HttpResponse(json.dumps({'task_id': wh_task.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')


def get_whois(request, id):
    if request.is_ajax() and request.method == 'GET':
        whoiss = Whois.objects.filter(device_id=id)

        response_data = serializers.serialize('json', whoiss)

        return HttpResponse(response_data, content_type="application/json")
