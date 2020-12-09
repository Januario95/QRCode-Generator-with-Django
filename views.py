from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, login, logout
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin
)
from django.contrib import messages
from .forms import (
    MovieSearchForm, LoginForm,
    RegisterForm, OrderByForm
)
from .models import Searches
import requests
import json


def logout_view(request):
    logout(request)
    return redirect('/movie/login/')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,
                            username=username,
                            password=password)
        print(user is not None)
        if user is not None:
            login(request, user)
            return redirect('/movie/')
        else:
            return redirect('/movie/login/')
    else:
        form = LoginForm()
    return render(request,
           'movies/login.html',
           {'form': form})


class MovieDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'movies/movie_details.html'
    form_class = OrderByForm
    login_url = '/movie/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        form = self.form_class
        movies = Searches.objects.filter(user=request.user)
        movies = movies.order_by('-number_of_searches')
        return render(request,
                     self.template_name,
                     {'movies': movies,
                      'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        movies = Searches.objects.filter(user=request.user)
        if form.is_valid():
            order_by = form.cleaned_data.get('order_by')
            ordering = form.cleaned_data.get('ordering')
            if ordering == 'ascending':
                movies = movies.order_by(f'{order_by}')
            elif ordering == 'descending':
                movies = movies.order_by(f'-{order_by}')

        return render(request,
                     self.template_name,
                     {'movies': movies,
                      'form': form})



class RegisterView(TemplateView):
    template_name = 'movies/register.html'
    redirect_field_name = 'redirect_to'
    form_class = RegisterForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request,
                      self.template_name,
                      {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(form.cleaned_data)
            user = User.objects.create_user(username=username,
                                            email=email)
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, 'Your account was created successfully. You can now login')
            return redirect('/movie/login/')
        else:
            messages.warning(request, 'Wrong values we given')
            form = self.form_class()
            return render(request,
                          self.template_name,
                          {'form': form})


class MovieSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'movies/movie.html'
    form_class = MovieSearchForm
    login_url = '/movie/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        user = Searches.objects.filter(user=request.user)
        number_of_searches = user.count()
        form = self.form_class()
        return render(request, self.template_name,
                      {'form': form,
                       'number_of_searches': number_of_searches})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        movies = []
        if form.is_valid():
            query = form.cleaned_data.get('query')
            url = f'https://www.omdbapi.com/?s={query}&apikey=30edcdd8'
            print(url)
            r = requests.get(url)
            json_data = r.json()
            if json_data.get('Response') == 'False':
                print('Too many results')
            else:
                movies = json_data.get('Search')
                movie = Searches.objects.filter(search=query,
                                user=request.user)
                if movie.exists():
                    movie_ = movie.first()
                    movie_.number_of_searches += 1
                    movie_.save()
                else:
                    search = Searches.objects.create(
                        user=request.user,
                        search=query,
                        number_of_searches=1
                    )
                    search.save()
                #print(json.dumps(json_data.get('Search'), indent=4))

            form = self.form_class()
            user = Searches.objects.filter(user=request.user)
            number_of_searches = user.count()
            return render(request, self.template_name,
                     {'form': form,
                      'movies': movies,
                      'number_of_searches': number_of_searches})
        else:
            form = self.form_class()
            user = Searches.objects.filter(user=request.user)
            number_of_searches = user.count()
            return render(request, self.template_name,
                        {'form': form,
                         'number_of_searches': number_of_searches})


