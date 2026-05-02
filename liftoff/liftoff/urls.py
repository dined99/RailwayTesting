from django.contrib import admin
from django.urls import path
from railwayapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.contractors, name='contractors'),
    path('contractors/', views.contractors, name='contractors_list'),
    path('contractors/map/data/', views.contractor_map_data, name='contractor_map_data'),
]
