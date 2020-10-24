from django import forms


class QRGeneratorForm(forms.Form):
    title = forms.CharField(max_length=80)
    url = forms.URLField(label='You website',
                required=True)
    # image_url = forms.CharField()

