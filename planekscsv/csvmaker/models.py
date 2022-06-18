from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings

from planekscsv.utils import random_string_generator
# Create your models here.

User = settings.AUTH_USER_MODEL

TYPE_CHOICES = (
    ('company', 'Company'),
    ('fullname', 'Full Name'),
    ('address', 'Address'),
    ('email', 'Email'),
    ('phone', 'Phone Number'),
    ('url', 'URL')
)

class Column(models.Model):
    title = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Column named {self.title}'

DELIMITERS_CHOICES = (
    (';', 'Semicolon (;)'),
    (',', 'Comma (,)')
)

STRING_QUOTE_CHOICES = (
    ('"', 'Double quote (")'),
    ("'", "Single quote (')")
)

class Schema(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(unique=True, allow_unicode=True)
    delimiter = models.CharField(max_length=1, choices=DELIMITERS_CHOICES, default=',')
    string_quote = models.CharField(max_length=1, choices=STRING_QUOTE_CHOICES, default='"')
    columns = models.ManyToManyField(Column)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Schema named {self.title}"

    def get_absolute_url(self):
        return reverse('csvmaker:single', kwargs={'slug': self.slug})

    @property
    def all_datasets(self):
        return self.datasets.all()


def pre_save_slug_receiver(instance, sender, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title) + random_string_generator(5)

pre_save.connect(pre_save_slug_receiver, sender=Schema)

DATASET_STATUS_CHOICES = (
    ('none', 'None'),
    ('processing', 'Processing'),
    ('ready', 'Ready')
)

class Dataset(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.SET_NULL, null=True, related_name='datasets')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=DATASET_STATUS_CHOICES, default='none')
    num_rows = models.PositiveIntegerField(default=0)
    filename = models.CharField(max_length=200, blank=True, null=True)
    path_to_file = models.CharField(max_length=200, blank=True, null=True)
    task_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'Dataset {self.id} from schema {self.schema.title}'
