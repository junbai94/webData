from django import forms

class FutDailyForm(forms.Form):
    instID = forms.CharField(label='Future Ticker', max_length=100)