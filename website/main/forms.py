from django import forms

class UploadFileForm(forms.Form):
    xml_upload = forms.FileField(label='Upload xml')
