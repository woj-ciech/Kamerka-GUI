from django import forms


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


class DevicesNearbyForm(forms.Form):
    id = forms.CharField(max_length=100)
