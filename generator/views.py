from django.shortcuts import render

import os
from .forms import QRGeneratorForm
import qrcode


def make_qrcode(title, url):
    print(os.getcwd())
    img = qrcode.make(url)
    path = os.getcwd() + "\\generator\\static\\generator\\Images\\"
    file = f'{title}.jpg'
    path += file
    img.save(path)
    return file

def qrcode_generator(request):
    url_exist = False
    url = ""
    file = ""
    if request.method == 'POST':
        form = form = QRGeneratorForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            title = cd.get('title')
            url = cd.get('url')
            file = make_qrcode(title, url)
            url_exist = True


    else:
        form = QRGeneratorForm()

    return render(request,
                'generator/qrcode_generator.html',
                {"form": form,
                 "url_exist": url_exist,
                 "url": url,
                 "file": f'generator/Images/{file}'})
