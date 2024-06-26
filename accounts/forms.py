from django import forms

from accounts.models import Address, State, PersonalDetails


class EmailForm(forms.Form):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'style': 'width: 100%; height: 45px; padding: 10px; outline: none; border: 2px solid #ccc; ',
            'class': 'email-input'
        })
    )


class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email address', widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                                   'required': True}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                    'required': True}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                            'required': True}))


class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = PersonalDetails
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': '',
            'last_name': '',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control mx-auto', 'placeholder': 'First Name*',
                                                 'style': 'width: 80% !important', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control mx-auto', 'placeholder': 'Last Name*',
                                                'style': 'width: 80% !important', 'required': True}),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'class': 'form-control bg-secondary text-white', 'required': True})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mt-3', 'placeholder': 'Password',  'style': 'width: 100% !important',  'required': True})
    )


class EditBasicDetailsForm(forms.ModelForm):
    class Meta:
        model = PersonalDetails
        fields = ['first_name', 'middle_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(EditBasicDetailsForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


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
        if user and user.is_authenticated:  # Checking if the user is authenticated
            try:
                user_state = user.addresses.first().state
            except AttributeError:
                # Handle the case where the user doesn't have any addresses or the state is not set
                user_state = None
            self.fields['state'].queryset = State.objects.all()
            self.fields['state'].initial = user_state

        # Add custom attributes and styling to individual fields
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'firstName',
            'style': 'width: 100% !important;',
            'name': 'first_name'
        })

        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'lastName',
            'style': 'width: 100% !important;',
            'name': 'last_name'
        })

        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'id': 'address',
            'style': 'width: 100% !important;',
            'placeholder': 'Enter your Address',
            'name': 'address'
        })

        self.fields['additional_info'].widget.attrs.update({
            'class': 'form-control',
            'id': 'additional_info',
            'style': 'width: 100% !important;',
            'placeholder': 'Enter Additional Information',
            'name': 'additional_info'
        })

        self.fields['state'].widget.attrs.update({
            'class': 'form-select',
            'id': 'state',
            'style': 'width: 100% !important',
            'name': 'state'
        })


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': True})
    )


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control bg-secondary text-white', 'readonly': 'readonly'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control mt-3', 'style': 'width: 100% !important;', 'placeholder': 'Password',
                   'id': 'Password1'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control mt-3', 'style': 'width: 100% !important;',
                                          'placeholder': 'Confirm Password', 'id': 'password2'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")