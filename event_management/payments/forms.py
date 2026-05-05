from django import forms
from .models import WithdrawalRequest

class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount_requested', 'bank_name', 'account_number', 'account_name']
        widgets = {
            'amount_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. GTBank'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10 digits'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Account Name'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount_requested(self):
        amount = self.cleaned_data.get('amount_requested')
        if self.user and amount > self.user.released_balance:
            raise forms.ValidationError(f"Your withdrawable balance is only ₦{self.user.released_balance}")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
