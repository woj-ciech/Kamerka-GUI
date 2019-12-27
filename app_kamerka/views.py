import ast
import json
from collections import Counter

import pycountry
from celery.result import AsyncResult
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app_kamerka import forms
from app_kamerka.models import Search, Device, DeviceNearby, FlickrNearby, ShodanScan, BinaryEdgeScore, Whois, \
    TwitterNearby
from kamerka.tasks import shodan_search, devices_nearby, twitter_nearby_task, flickr, shodan_scan_task, \
    binary_edge_scan, whoisxml, check_credits


# Create your views here.

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

    context = {'device': all_devices,
               'nearby': nearby,
               'flickr': flickr,
               "shodan": shodan,
               'google_maps_key': google_maps_key}

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

        for i in shodan_scan2:
            try:
                i.tags = ast.literal_eval(i.tags)
            except:
                pass
        response_data = serializers.serialize('json', shodan_scan2)

        return HttpResponse(response_data, content_type="application/json")


def get_nearby_devices(request, id):
    if request.is_ajax() and request.method == 'GET':
        nearby_devices = DeviceNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', nearby_devices)

        return HttpResponse(response_data, content_type="application/json")


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
