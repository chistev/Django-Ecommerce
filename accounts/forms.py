from django import forms

from accounts.models import Address, State


class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email address', widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                                   'required': True}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                    'required': True}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                            'required': True}))


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': True})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'address', 'additional_info', 'state', 'city']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve the user from kwargs
        super(AddressForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].label = "First Name"
        self.fields['last_name'].label = "Last Name"
        self.fields['address'].label = "Delivery Address"
        self.fields['additional_info'].label = "Additional Information"

        # Populate the state field with the user's existing state
        if user.is_authenticated:  # Checking if the user is authenticated
            try:
                # Assuming there's a direct ForeignKey relationship between CustomUser and State
                user_state = user.addresses.first().state
            except AttributeError:
                # Handle the case where the user doesn't have any addresses or the state is not set
                user_state = None
            self.fields['state'].queryset = State.objects.all()  # Adjust this queryset based on your State model
            self.fields['state'].initial = user_state

        # Add custom attributes and styling to individual fields
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'firstName',  # ID for the first name field
            'style': 'width: 350px !important;',
            'name': 'first_name'
        })

        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'lastName',  # ID for the last name field
            'style': 'width: 350px !important;',
            'name': 'last_name'
        })

        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'id': 'address',  # ID for the last name field
            'style': 'width: 100% !important;',
            'placeholder': 'Enter your Address',
            'name': 'address'
        })

        self.fields['additional_info'].widget.attrs.update({
            'class': 'form-control',
            'id': 'additional_info',  # ID for the last name field
            'style': 'width: 100% !important;',
            'placeholder': 'Enter Additional Information',
            'name': 'additional_info'
        })

        self.fields['state'].widget.attrs.update({
            'class': 'form-select',
            'id': 'state',
            'style': 'width: 350px !important',
            'name': 'state'
        })

