import os
import mimetypes

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Schema, Column, Dataset
from .forms import SchemaForm, ColumnForm
from .tasks import generate_dataset as create_csv
# Create your views here.

class SchemaList(generic.ListView):
    model = Schema
    template_name = 'csvmaker/list.html'
    context_object_name = 'schemas'



def new_column(request):
    request.session['col_ids'] = request.session.get('col_ids', [])
    form = ColumnForm(request.POST or None)
    if form.is_valid():
        col_obj = form.save()
        if request.is_ajax:
            request.session['col_ids'].append(col_obj.id)
    return redirect('csvmaker:new')


def new_schema(request):
    schema_form = SchemaForm(request.POST or None)
    column_form = ColumnForm(request.POST or None)

    if schema_form.is_valid():

        schema_obj = schema_form.save(commit=False)
        schema_obj.author = request.user
        schema_obj.save()
        
        created_columns = Column.objects.filter(id__in=request.session['col_ids'])

        for item in created_columns:
            schema_obj.columns.add(item)
        schema_obj.save()

        del request.session['col_ids']
        return redirect('csvmaker:all')

    context = {
        'form': schema_form,
        'column_form': column_form,
    }

    return render(request, 'csvmaker/new.html', context)


def delete_schema(request, id):
    schema_obj = get_object_or_404(Schema, id=id)
    schema_obj.delete()
    return redirect('csvmaker:all')



def single_schema_datasets(request, id):
    schema_obj = get_object_or_404(Schema, id=id)
    datasets = schema_obj.all_datasets
    # for i in datasets:
    #     if i.status != 'none':
    #
    context = {
        'schema': schema_obj,
        'datasets': datasets
    }
    return render(request, 'csvmaker/single.html', context)



def generate_dataset(request, id):
    schema_obj = get_object_or_404(Schema, id=id)

    num_rows = request.POST.get('num_rows', None)
    dataset_obj = Dataset.objects.create(schema=schema_obj, num_rows=num_rows, status='processing')

    if num_rows is not None:
        task = create_csv.delay(id, num_rows=num_rows)
        dataset_obj.task_id = task.task_id
        dataset_obj.save()


    return redirect('csvmaker:single', id=schema_obj.id)



def download_dataset(request, id):
    dataset_obj = get_object_or_404(Dataset, id=id)
    file_path = dataset_obj.path_to_file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
            return response
    raise Http404
