from django.contrib import admin
from django.urls import path
from railwayapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.contractors, name='contractors'),
    path('contractors/', views.contractors, name='contractors_list'),
    path('contractors/map/data/', views.contractor_map_data, name='contractor_map_data'),
    path('contractors/add/', views.add_contractor, name='add_contractor'),
    path('contractors/<int:staff_id>/', views.contractor_detail, name='contractor_detail'),
    path('contractors/<int:staff_id>/upload/', views.upload_contractor_file, name='upload_contractor_file'),
    path('contractors/files/<int:file_id>/download/', views.download_contractor_file, name='download_contractor_file'),
    path('contractors/files/<int:file_id>/delete/', views.delete_contractor_file, name='delete_contractor_file'),
]
