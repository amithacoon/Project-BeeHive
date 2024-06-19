# forms.py in the csvviewer app

from django import forms

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV or XLSX file \n')
