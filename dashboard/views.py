import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.http import JsonResponse



from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model

from django.db.models import Sum
from django.utils import timezone
from collections import defaultdict
import calendar
from django.db.models.functions import ExtractMonth

from django.http import Http404


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from functools import reduce

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from app.models import Order, Dish, Restaurant





User = get_user_model()

# ----------------------------- DASHBOARD AUTH PAGES ----------------------------------


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    
    return render(request, "dashboard/pages-sign-up.html", {})


# Login and Logout pages
@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    
    return render(request, "dashboard/pages-sign-in.html", {})



# Login and Log out API

# ----------------------------- DASHBOARD AUTH PAGES END ----------------------------------


def get_first_name_automatically(username: str):
    name_list = username.split(" ")
    if len(name_list) > 1:
        return name_list[0]
    else:
        return username

@login_required
def dashboard_home(request):

    user = request.user

    # Dishes
    dishes = Dish.objects.all()


    # Orders
    orders = Order.objects.all()
    order_count = orders.count()
    # Customers
    customers = User.objects.filter(role="customer")
    customer_count = customers.count()
    # Drivers
    drivers = User.objects.filter(role="logistics")
    driver_count = drivers.count()
    # Restaurants
    restaurants = User.objects.filter(role="chef")
    restaurant_count = restaurants.count()

    username = get_first_name_automatically(user.profile.name)

    return render(request, 'dashboard/index.html', {
        "order_count": order_count,
        "customer_count": customer_count,
        "restaurant_count": restaurant_count,
        "driver_count": driver_count,
        "username": username,
    })

@login_required
def users_list(request):
    users = User.objects.all().order_by("-pk")
    return render(request, 'dashboard/users_list.html', {
        "users": users
    })


@login_required
def users_details(request, pk):
    try:
        user_obj = User.objects.get(pk=pk)

        print(user_obj.email)
    except User.DoesNotExist:
        raise Http404
    
    
    
    return render(request, 'dashboard/users_details.html', {
        "user_obj": user_obj,
    })

def users_create(request):

    return render(request, 'dashboard/users_create.html', {
    })

def users_edit(request, pk):
    try:
        user_obj = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise Http404
    
    return render(request, 'dashboard/users_edit.html', {
        "user_obj": user_obj,
        "user_first_name":  user_obj.profile.name.split(" ")[0] if user_obj.profile.name.split(" ")[0] else "",
        "user_last_name": user_obj.profile.name.split(" ")[1] if user_obj.profile.name.split(" ")[1] else "",
    })

@login_required
def restaurants_list(request):
    restaurants = Restaurant.objects.all().order_by("-pk")
    return render(request, 'dashboard/restaurants_list.html', {
        "restaurants": restaurants
    })


@login_required
def restaurant_details(request, pk):
    try:
        restaurant = Restaurant.objects.get(id=pk)
        dishes_count = len(restaurant._dishes)
    except Restaurant.DoesNotExist:
        raise Http404
    
    return render(request, 'dashboard/restaurant_detail.html', {
        "restaurant": restaurant,
        "dishes_count": dishes_count,
    })

def restaurant_edit(request, pk):
    try:
        restaurant = Restaurant.objects.get(id=pk)
        dishes_count = len(restaurant._dishes)
    except Restaurant.DoesNotExist:
        raise Http404
    
    restaurant_users = User.objects.filter(role="chef")


    
    return render(request, 'dashboard/restaurant_edit.html', {
        "restaurant": restaurant,
        "dishes_count": dishes_count,
        "restaurant_users": restaurant_users,
    })


def restaurant_create(request):

    return render(request, 'dashboard/restaurant_create.html', {
    })


@login_required
def profile_view(request):
    return render(request, 'dashboard/profile.html', {
       
    })


@login_required
def dishes_list(request):
    return render(request, 'dashboard/dishes_list.html', {
       
    })


@login_required
def orders_list(request):
    return render(request, 'dashboard/orders_list.html', {
       
    })


@login_required
def customers_list(request):
    return render(request, 'dashboard/customer_list.html', {
       
    })


@login_required
def drivers_list(request):
    return render(request, 'dashboard/drivers_list.html', {
       
    })


