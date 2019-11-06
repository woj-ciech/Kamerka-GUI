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
        if coordinates_form.is_valid():
            coordinates = coordinates_form.cleaned_data['coordinates']
            search = Search(coordinates=coordinates_form.cleaned_data['coordinates'],
                            coordinates_search=request.POST.getlist('coordinates_search'))

            search.save()
            xd = shodan_search.delay(fk=search.id, coordinates=coordinates,
                                     coordinates_search=request.POST.getlist('coordinates_search'))

            request.session['task_id'] = xd.task_id

            return HttpResponseRedirect('index')

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

            xd = shodan_search.delay(fk=search.id, country=code, ics=post, all_results=all_results)
            request.session['task_id'] = xd.task_id

            return HttpResponseRedirect('index')
            # return render(request, 'index.html', context)

        # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.CountryForm()
        return render(request, 'search_main.html', {'form': form})

    # return render(request, "index.html", {})


def index(request):
    a = Device.objects.all()
    w = Search.objects.filter().order_by('-id')[:5]
    ics_len = Device.objects.filter(category="ics")
    coordinates_search_len = Device.objects.filter(category="coordinates")
    search_len = Search.objects.all()
    task = request.session.get('task_id')
    port = Device.objects.values('port').annotate(c=Count('port')).order_by('-c')[:7]
    k = list(port)
    vulns1 = Device.objects.exclude(vulns__isnull=True).exclude(vulns__exact='')

    tab = []

    for i in vulns1:
        tab.append(ast.literal_eval(i.vulns))

    cves = []
    for i in tab:
        for j in i:
            cves.append(j)

    d = {}
    c = Counter(cves)
    for key, value in c.items():
        d[key] = value

    sort = sorted(d.items())[:7]

    countries = {}
    for i in search_len:
        countries[i.country] = "1"

    for j in w:
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

    context = {'device': a,
               "search": w,
               "ics": ics_len,
               "coordinates": coordinates_search_len,
               "ports": k, "countries": countries,
               'vulns': sort,
               "task_id": task,
               "search_len": search_len,
               "credits": credits}

    # print(context)

    return render(request, 'index.html', context)


def devices(request):
    a = Device.objects.all()

    for i in a:
        try:
            i.indicator = ast.literal_eval(i.indicator)
        except:
            pass

    context = {"devices": a}

    return render(request, "devices.html", context=context)


def map(request):
    a = Device.objects.all()

    google_maps_key = keys['keys']['google_maps']

    context = {"devices": a, 'google_maps_key': google_maps_key}

    return render(request, "map.html", context=context)


def results(request, id):
    a = Device.objects.filter(search_id=id)
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

    vulns1 = Device.objects.exclude(vulns__isnull=True).exclude(vulns__exact='')

    tab = []

    for i in vulns1:
        tab.append(ast.literal_eval(i.vulns))
    cves = []
    for i in tab:
        for j in i:
            cves.append(j)

    d = {}
    c = Counter(cves)
    for key, value in c.items():
        d[key] = value

    sort = sorted(d.items())[:7]

    for i in a:
        try:
            i.indicator = ast.literal_eval(i.indicator)

        except:
            pass


    context = {'search': a,
               'ports': ports_list,
               "vulns": sort,
               "category": categories_list,
               "city": cities_list,
               'google_maps_key': google_maps_key}

    return render(request, 'results.html', context)


def history(request):
    a = Search.objects.all()

    for i in a:
        try:
            i.coordinates_search = ast.literal_eval(i.coordinates_search)
        except Exception as e:
            print(e)

        try:
            i.ics = ast.literal_eval(i.ics)
        except Exception as e:
            print(e)

    context = {'history': a}
    return render(request, 'history.html', context)


def device(request, id, device_id, ip):
    a = Device.objects.get(search_id=id, id=device_id)
    nearby = DeviceNearby.objects.filter(device_id=a.id)
    flickr = FlickrNearby.objects.filter(device_id=a.id)
    shodan = ShodanScan.objects.filter(device_id=a.id)
    google_maps_key = keys['keys']['google_maps']

    try:
        a.indicator = ast.literal_eval(a.indicator)
    except:
        pass

    context = {'device': a,
               'nearby': nearby,
               'flickr': flickr,
               "shodan": shodan,
               'google_maps_key': google_maps_key}

    return render(request, 'device.html', context)


def nearby(request, id, query):
    if request.is_ajax() and request.method == 'GET':
        a = Device.objects.filter(id=id)
        device_nearby_task = devices_nearby.delay(lat=a[0].lat, lon=a[0].lon, id=id, query=query)
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

        be = ShodanScan.objects.filter(device_id=id)

        if be:
            print('already')
            return HttpResponse(json.dumps({'Error': "Already in database"}), content_type='application/json')

        shodan = shodan_scan_task.delay(id=id)
        return HttpResponse(json.dumps({'task_id': shodan.id}), content_type='application/json')
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
        a = ShodanScan.objects.filter(device_id=id)

        for i in a:
            try:
                i.tags = ast.literal_eval(i.tags)
            except:
                pass
        response_data = serializers.serialize('json', a)

        return HttpResponse(response_data, content_type="application/json")


def get_nearby_devices(request, id):
    if request.is_ajax() and request.method == 'GET':
        a = DeviceNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)

        return HttpResponse(response_data, content_type="application/json")


def get_flickr_results(request, id):
    if request.is_ajax() and request.method == 'GET':
        a = FlickrNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)

        return HttpResponse(response_data, content_type="application/json")


def get_flickr_coordinates(request, id):
    if request.is_ajax() and request.method == 'GET':
        a = FlickrNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)

        return HttpResponse(response_data, content_type="application/json")


def get_nearby_devices_coordinates(request, id):
    if request.is_ajax() and request.method == 'GET':
        a = DeviceNearby.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)

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
        a = BinaryEdgeScore.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)

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
        a = Whois.objects.filter(device_id=id)

        response_data = serializers.serialize('json', a)

        return HttpResponse(response_data, content_type="application/json")
