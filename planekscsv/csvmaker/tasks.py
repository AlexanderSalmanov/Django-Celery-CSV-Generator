from __future__ import absolute_import, unicode_literals
from django.core.cache import cache

from planekscsv.celery import app
from celery.utils.log import get_task_logger
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from csv import reader, writer
from faker import Faker

from .models import Dataset, Schema
from planekscsv.utils import random_string_generator

logger = get_task_logger(__name__)

@shared_task(bind=True)
# @app.task(name='generate_dataset')
def generate_dataset(self, schema_id, num_rows):
    progress_recorder = ProgressRecorder(self)

    iterations = int(num_rows) #explicitly cast form input value into an integer
    schema = Schema.objects.get(id=schema_id) # retrieve schema object
    logger.info(f'Generated schema csv file with {num_rows} rows') # log info to celery terminal window
    dataset = Dataset.objects.get(schema=schema, status='processing', num_rows=num_rows) # getting dataset object associated to current schema object
    fakegen = Faker()
    columns = schema.columns.all().order_by('order') # getting all columns related to current schema and sort them by 'order' attribute

    type_lookup = {
        'fullname': fakegen.name, # invoking functions every time we're calling them, not just retrieving returned value if it would be like fakegen.foo() (1000 calls - same value) not fakegen.foo (1000 calls - 1000 values)
        'company': fakegen.company, # same thing along the whole dict
        'url': fakegen.url,
        'address': fakegen.address,
        'phone': fakegen.phone_number,
        'email': fakegen.email
    }
    types = [key for key in type_lookup]

    filename = f'{schema.id}_{random_string_generator(7)}.csv'

    filepath = f'csvmaker/generated_files/{filename}'
    with open(f'{filepath}', 'w', newline='') as f:
        dataset.status = 'processing' # modifying dataset status
        dataset.save()
        csv_writer = writer(f)
        csv_writer.writerow([i.title for i in columns]) #Writing column headers
        for i in range(iterations):
            csv_writer.writerow([type_lookup.get(i.type)() for i in columns if i.type in list(type_lookup.keys())]) #Writing column data
            progress_recorder.set_progress(i + 1, iterations, description=f'On {i+1} row...') #setting progress on progress_recorder object

        dataset.path_to_file = filepath # assigning important file IO values to dataset object
        dataset.filename = filename
        dataset.status = 'ready' # finally, setting dataset.status to 'ready' meaning all manipulations with it are done
        dataset.save()
        # cache.set(self.request.id, dataset.id)
        # print(cache)
