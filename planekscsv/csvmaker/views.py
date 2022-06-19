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

    def get_queryset(self):
        return Schema.objects.filter(author=self.request.user)


def new_column(request):
    """
    View for creating columns associated to schemas. AJAX-ifyed to prevent the
    page from refreshing every time the new column is created.
    To store all columns created during the schema form usage, we look for the session variable,
    and if it's not present, then we default it to be an empty list. After creating the column,
    we append its id to the session variable.
    """
    request.session['col_ids'] = request.session.get('col_ids', [])
    form = ColumnForm(request.POST or None)
    if form.is_valid():
        col_obj = form.save()
        if request.is_ajax:
            request.session['col_ids'].append(col_obj.id)
    return redirect('csvmaker:new')


def new_schema(request):
    """
    View for creating schemas and columns related to it.
    The trickiest part of this view is associating multiple columns to one schema
    without refreshing the form page. To implement this, every single column is created
    via separate view, which, upon submitting, redirects the user back to the form page.
    All columm ids are stored in a session variable. This variable gets deleted after
    the scheme is created so that previous column entries are not included to the
    new schema object.
    """
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
    """
    Simple redirect view for deleting schemas. Works instantly with no conformations
    thanks to ajax-ifying the view.
    """
    schema_obj = get_object_or_404(Schema, id=id)
    schema_obj.delete()
    return redirect('csvmaker:all')



def single_schema_datasets(request, id):
    """
    Simple view which shows all datasets related to each specific schema.
    Combination of schema_detail-type view and dataset_list-type view.
    """
    schema_obj = get_object_or_404(Schema, id=id)
    datasets = schema_obj.all_datasets

    context = {
        'schema': schema_obj,
        'datasets': datasets
    }
    return render(request, 'csvmaker/single.html', context)



def generate_dataset(request, id):
    """
    View implementing csv-file generate feature.
    The most important parts are:
        CREATING THE DATASET_OBJ IN THE VIEW,
        AND RETRIEVING IT IN THE TASK! This detail
        prevents generating redundant dataset objects.
        Initiate the task and assign it to a variable.
        Then assigning the value of task.task_id to a specific dataset_obj
        to enable progress bars on every single dataset object.
    """
    schema_obj = get_object_or_404(Schema, id=id)

    num_rows = request.POST.get('num_rows', None)
    dataset_obj = Dataset.objects.create(schema=schema_obj, num_rows=num_rows, status='processing')

    if num_rows is not None:
        task = create_csv.delay(id, num_rows=num_rows)
        dataset_obj.task_id = task.task_id
        dataset_obj.save()


    return redirect('csvmaker:single', id=schema_obj.id)



def download_dataset(request, id):
    """
    Default view enabling file download feature.
    Retrivies file path related to specific dataset, and then downloading the file with corresponding file path.
    """
    dataset_obj = get_object_or_404(Dataset, id=id)
    file_path = dataset_obj.path_to_file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
            return response
    raise Http404
