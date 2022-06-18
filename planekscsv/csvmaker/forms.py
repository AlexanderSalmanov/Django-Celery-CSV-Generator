from django import forms
from .models import Schema, Column

class SchemaForm(forms.ModelForm):
    # colums_num = forms.IntegerField(label='Specify number of columns')
    class Meta:
        model = Schema
        fields = ['title', 'delimiter', 'string_quote']

class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['title', 'type', 'order']
