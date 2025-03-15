
from django.urls import path
from . import views
from . import api_views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    path("restaurants/", views.restaurants_list, name="restaurants_list"),
    path("restaurants/<int:pk>/", views.restaurant_details, name="restaurant_details"),
    path("restaurants/edit/<int:pk>/", views.restaurant_edit, name="restaurant_edit"),
    path("restaurants/create/", views.restaurant_create, name="restaurant_create"),

    path("users/", views.users_list, name="users_list"),
    path("users/create/", views.users_create, name="users_create"),
    path("users/edit/<int:pk>/", views.users_edit, name="users_edit"),
    path("users/<int:pk>/", views.users_details, name="users_details"),

    path("dishes/", views.dishes_list, name="dishes_list"),
    path("drivers/", views.drivers_list, name="drivers_list"),
    path("customer/", views.customers_list, name="customers_list"),
    path("orders/", views.orders_list, name="orders_list"),
    path("profile/", views.profile_view, name="profile"),

    path("logout/", views.LogoutView, name="logout"),


    # API VIEWS
    path("api/register/", api_views.dashboard_register_api, name="dashboard_register_api"),
    path("api/login/", api_views.dashboard_login_api, name="dashboard_login_api"),
    path("api/restaurant/create/", api_views.restaurant_create_api, name="restaurant_create_api"),
    path("api/restaurant/edit/<int:pk>/", api_views.restaurant_edit_api, name="restaurant_edit_api"),

    path("api/users/create/", api_views.users_create_api, name="users_create_api"),
    path("api/users/edit/<int:pk>/", api_views.user_update_api, name="user_update_api"),

]


