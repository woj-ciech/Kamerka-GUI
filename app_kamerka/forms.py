from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
#
class CoordinatesForm(forms.Form):
    coordinates = forms.CharField(max_length=100)

class CountryForm(forms.Form):
    country = forms.CharField(max_length=100)
    all = forms.BooleanField(required=False)
    own_database = forms.BooleanField(required=False)

class CountryHealthcareForm(forms.Form):
    country_healthcare = forms.CharField(max_length=100)
    all = forms.BooleanField(required=False)
    own_database = forms.BooleanField(required=False)

class InfraForm(forms.Form):
    country_infra = forms.CharField(max_length=100)
    all = forms.BooleanField(required=False)
    own_database = forms.BooleanField(required=False)

class DevicesNearbyForm(forms.Form):
    id = forms.CharField(max_length=100)
