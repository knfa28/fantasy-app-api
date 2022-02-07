from django.urls import path, include
from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from apps.fantasy.views import *

router = DefaultRouter()
router.register(r'team', TeamViewSet)
router.register(r'athlete/api', AthleteAPIViewSet)
router.register(r'athlete', AthleteViewSet)
router.register(r'game', GameViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
