from django.urls import path
from . import views

app_name = 'csvmaker'

urlpatterns = [
    path('', views.SchemaList.as_view(), name='all'),
    path('datasets/<int:id>/', views.single_schema_datasets, name='single'),
    path('new/', views.new_schema, name='new'),
    path('new/col/', views.new_column, name='new_col'),
    path('delete/<int:id>/', views.delete_schema, name='delete'),
    path('generate/<int:id>/', views.generate_dataset, name='generate'),
    path('download/<int:id>/', views.download_dataset, name='download')
]
