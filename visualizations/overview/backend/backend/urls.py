from overview.views import PatientListView, ChartView
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("patient_list", cache_page(60*15)(PatientListView.as_view()), name="patient_list"),
    path("chart/<int:patient_id>", ChartView.as_view(), name="chart"),
]
