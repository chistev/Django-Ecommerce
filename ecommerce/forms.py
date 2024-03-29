from django import forms


class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search Products', widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}))
