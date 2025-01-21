from django.urls import path, include
from . import views as primary_views
from . import action_views as secondary_views

from rest_framework.routers import DefaultRouter

# from .action_views import OrderViewSet, OrderItemViewSet, DishViewSet


# router = DefaultRouter()
# router.register(r'orders', OrderViewSet)
# router.register(r'orderitems', OrderItemViewSet)
# router.register(r'dishes', DishViewSet)


urlpatterns = [
    # Primary Views
    path('', primary_views.HomeAPIViewList.as_view(), name="general_api_view"),


    path('categories/', primary_views.CategoryViewList.as_view(), name="category_list"),
    path('categories/<int:pk>/', primary_views.CategoryViewDetails.as_view(), name="category_detail"),

    path('dishes/', primary_views.DishesViewList.as_view(), name="dish_list"),
    path('dishes/<int:pk>/', primary_views.DishDetailView.as_view(), name="dish_detail"),
    path('dishes/<int:pk>/ratings/', primary_views.DishDetailRatingView.as_view(), name="dish_ratings"),

    path("restaurants/", primary_views.ResturantViewList.as_view(), name="restaurant_list"),
    path("restaurants/<int:pk>/", primary_views.RestaurantViewDetails.as_view(), name="restaurant_detail"),
    path('restaurants/<int:pk>/ratings/', primary_views.RestaurantDetailRating.as_view(), name="restaurant_ratings"),

    path("drivers/", primary_views.DriversViewList.as_view(), name="driver_list"),
    path("drivers/<int:pk>/", primary_views.DriverViewDetails.as_view(), name="driver_detail"),
    path("drivers/<int:pk>/ratings/", primary_views.DriverDetailRating.as_view(), name="driver_ratings"),

    path('payment/intent/', secondary_views.payment_intent_stripe, name="payment_intent_stripe"),

    # Secondary Views
    # path('customers/', include(router.urls)),
    path('orders/', secondary_views.OrderCustomerListView.as_view(), name="customer_order"),
    path('orderitems/', secondary_views.OrderItemsListForAllUsers.as_view(), name="orderitems_list"),
    path('orderitems/<int:pk>/', secondary_views.OrderItemsDetailsForAllUsers.as_view(), name="orderitems_details"),
    path('orderitems/drivers/assign/', secondary_views.assign_driver_to_orderitem, name="assign_driver_to_orderitems"),
    
    path('ingredients/', primary_views.IngredientViewList.as_view(), name="ingredient_view_list"),
    path('ingredients/<int:pk>/', primary_views.IngredientDetailView.as_view(), name="ingredient_view_detail"),

] 





