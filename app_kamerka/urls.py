from django.urls import path, include
from app_kamerka import views

urlpatterns = [
    path('', views.search_main, name='search_main'),
    path('index', views.index, name='index'),
    path('history', views.history, name='history'),
    path('map', views.map, name='map'),
    path('devices', views.devices, name='devices'),
    path('sources', views.sources, name='sources'),

    path("results/<id>", views.results, name='results'),

    path("results/<id>/<device_id>/<ip>", views.device, name='device'),
    path(r'^celery-progress/', include('celery_progress.urls')),
    path("<id>/nearby/<query>", views.nearby, name='nearby'),
    path("<id>/update_coordinates/<coordinates>", views.update_coordinates, name='update_coordinates'),

    path("<id>/twitter/nearby", views.twitter_nearby, name='twitter_nearby'),
    path("<id>/twitter/show", views.twitter_show, name='twitter_show'),

    path("<id>/flickr/nearby", views.flickr_nearby, name='flickr_nearby'),
    path("<id>/shodan/scan", views.shodan_scan, name='shodan_scan'),
    path('get-task-info/', views.get_task_info, name="get_task_info"),
    path('get_flickr_results/<id>', views.get_flickr_results, name="get_flickr_results"),
    path('get_flickr_coordinates/<id>', views.get_flickr_coordinates, name="get_flickr_coordinates"),
    path('get_shodan_scan_results/<id>', views.get_shodan_scan_results, name="get_shodan_scan_results"),
    path('get_nearby_devices/<id>', views.get_nearby_devices, name="get_nearby_devices"),

    path('get_nearby_devices_coordinates/<id>', views.get_nearby_devices_coordinates,
         name="get_nearby_devices_coordinates"),
    path('get_binaryedge_score/<id>', views.get_binaryedge_score, name="get_binaryedge_score"),
    path('get_binaryedge_score_results/<id>', views.get_binaryedge_score_results, name="get_binaryedge_score_results"),
    path('whois/<id>', views.whois, name="whois"),
    path('get_whois/<id>', views.get_whois, name="get_whois"),

]
