from django.urls import path, include
# from rest_framework.authtoken import primary_views
from . import views as primary_views
from . import action_views as secondary_views

app_name = "authentication"

urlpatterns = [
    # Primary Views
    path('', primary_views.HomeAPIAuthViewList.as_view(), name="general_api_view"),
    path("token/", primary_views.CustomAuthToken.as_view(), name="token"),
    path("logout/", primary_views.logoutView, name="logout"),
    path("users/", primary_views.create_new_user, name="create_user"),

    path("users/verify/", primary_views.verify_user_upon_registration, name="verify_user"),
    path("users/verify/resend-code/", primary_views.verify_user_retry_code, name="verify_retry_code_user"),

    # Password
    path("users/reset/password/", primary_views.forget_password_view_email, name="forget_password_view_email"),
    path("users/reset/password/code/", primary_views.forget_password_view_code, name="forget_password_view_code"),
    path("users/change/password/", primary_views.change_user_password, name="change_user_password"),
    path("users/change/username/", primary_views.change_user_username, name="change_user_username"),

    path("users/me/", primary_views.get_current_user_profile, name="profile"),
    path("users/addresses/", primary_views.current_user_address_view, name="address_list"),
    path("users/addresses/<int:pk>/", primary_views.detail_user_address_view, name="address_detail"),

    # Secondary Views
    
    # Driver
    path('drivers/me/', secondary_views.get_driver_profile, name="driver_profile"),
    path("drivers/token/", secondary_views.login_driver, name="login_driver"),
    path("drivers/", secondary_views.create_driver, name="create_driver"),
    path("drivers/analytics/", secondary_views.driver_analytics, name="driver_analytics"),

    # Restaurant
    path('restaurants/me/', secondary_views.get_restaurant_profile, name="restaurant_profile"),
    
    # Restaurant withdrawal views
    path("restaurants/me/withdrawals/", secondary_views.retaurant_withdrawal_list_view, name="retaurant_withdrawal_list_view"),
    path("restaurants/me/withdrawals/<int:pk>/", secondary_views.retaurant_withdrawal_detail_view, name="retaurant_withdrawal_detail_view"),
    path('restaurants/me/deduct/', secondary_views.update_restaurant_balance, name="update_restaurant_profile_balance"),

    path("restaurants/token/", secondary_views.login_restaurant, name="login_restaurant"),
    path("restaurants/", secondary_views.create_restaurant, name="create_restaurant"),
    path("restaurants/analytics/", secondary_views.restaurant_analytics, name="restaurant_analytics"),
    
]




