from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from app.permissions import IsRestaurantUser, IsUserDriver
from app.models import Driver, Restaurant, OrderItem, Order, RestaurantWithdrawal
from authentication.models import UserProfile
from app.permissions import (
    IsUserVerified
)

from . import serializers
from app.serializers import (
    RestaurantSerializer,
    DriverSerializer,
    RestaurantRatingSerializer,
    
)



from .serializers import (
    RestaurantWithdrawalSerializer
)

from .helpers import check_email, is_valid_password


User = get_user_model()

from .helpers import (
    check_email, 
    is_valid_password, 
    generate_4_digit_code, 
    send_registration_code_mail, 
    check_if_code_matches,
)


# RESTAURANT AUTH VIEWS
@api_view(['POST'])
def login_restaurant(request):
    data = request.data
    kitchen_id = data.get("kitchen_id")
    password = data.get("password")

    if not kitchen_id:
        return Response({"message": "kitchen_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({"message": "password is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Search if the restaurant exists in either the Restaurant or User models
    try:
        user = User.objects.filter(username=kitchen_id).first()
    except User.DoesNotExist:
        user = None
        return Response({"message": "user does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        restaurant = Restaurant.objects.filter(kitchen_id=kitchen_id).first()
    except Restaurant.DoesNotExist:
        restaurant = None
        return Response({"message": "kitchen does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user:
        return Response({"message": "User does not exist. "}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.is_verified:
        return Response({"message": "User is not verified"}, status=status.HTTP_401_UNAUTHORIZED)
    
    if user and restaurant:
        # If both a user and a restaurant were found for that username/kitchen_id, check passwords
        if user.check_password(password):
            return Response({
                "token": user.auth_token.key, 
                "restaurant_id": restaurant.id,
                "user_id": user.id, 
                "kitchen_id": user.username,
                "permissions": {
                    "is_superuser": user.is_superuser,
                    "is_driver": user.role == "logistics",
                    "is_restaurant": user.role == "chef",
                    "is_customer": user.role == "customer"
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "user with kitchen id does exists"}, status=status.HTTP_400_BAD_REQUEST)



# This api view should only be assessed by admins | only admins can create kitchen
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def create_restaurant(request):
    """
    Creates Restaurant
    @payload: email, password
    """
    data = request.data
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "")
    address = data.get("address", "")
    description = data.get("description", "")


    # Create restaurant user
    # Check if user already exists
    # If user exists, do not create user
    if not description:
        return Response({
            "description": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    if not address:
        return Response({
            "address": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    if not name:
        return Response({
            "name": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    if not email:
        return Response({
            "email": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    elif not password:
        return Response({
            "password": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Check if email and password are valid entry
        email_valid_status = check_email(email)
        password_valid_status = is_valid_password(password)
        if email_valid_status.status == False:
            return Response({
                "email": [
                    error_message for error_message in email_valid_status.error_messages
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password_valid_status.status == False:
            return Response({
                "password": [
                    error_message for error_message in password_valid_status.error_messages
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        existing_user = User.objects.filter(email=email)
        if len(existing_user) > 1 or existing_user:
            return Response({
                "email": [
                    "User with email already exists."
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Finally create user Create user
            code = generate_4_digit_code()
            data.update({"role": "chef", "code": code})

            serializer = serializers.UserSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                # 
                if user.role == "chef":
                    restaurant = Restaurant.objects.filter(user=user).first()
                    profile = UserProfile.objects.filter(user=user).first()
                    
                    if restaurant:
                        restaurant.name = name
                        restaurant.address = address
                        restaurant.description = description
                        restaurant.save()

                        if profile:
                            profile.name = name
                            profile.save()
                        else:
                            pass
                    else:
                        pass
                # Object / Dictionary to be returned after user has been created
                user_details = {
                    "message": f"A verification code has been sent to {serializer.data.get('email')}.",
                    "user_id": serializer.data.get("id"),
                    "kitchen_id": serializer.data.get("username"),
                    "role": serializer.data.get("role"),

                }
                response_gotten_from_code = send_registration_code_mail(code, serializer.data.get('email'))
                # print("The response status I got from the code registration: ", response_gotten_from_code)

                return Response(user_details, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# RESTAURANT PROFILE
@api_view(['PUT', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def get_restaurant_profile(request):
    # Get User object
    # The case of user not existing given the token is highly unlikely
    # but additional checks must be made
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"message": "User was not found"}, status=status.HTTP_404_NOT_FOUND)
    # User must be a chef
    if user.role != "chef":
        return Response({"message": "User must be a chef. Permission denied."}, status=status.HTTP_401_UNAUTHORIZED)
    
    user_profile = UserProfile.objects.filter(user=user).first()
    restaurant_profile = Restaurant.objects.filter(user=user).first()

    # Requests request
    if request.method == 'GET':
        serializer = RestaurantSerializer(restaurant_profile)
        restaurant_details = {
            "id": serializer.data.get("id"),
            "name": serializer.data.get("name"),
            "description": serializer.data.get("description"),
            "ratings": serializer.data.get("ratings"),
            "image": serializer.data.get("image"),
            "image_url": restaurant_profile.image_url,
            "address": serializer.data.get("address"),
            "balance": serializer.data.get("balance"),
            "permissions": {
                "is_superuser": user.is_superuser,
                "is_driver": user.role == "logistics",
                "is_restaurant": user.role == "chef",
                "is_customer": user.role == "customer"
            }
        }
        return Response(restaurant_details, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data
        # name, description, image, address
        if data.get("kitchen_id"):
            return Response({"message":"You are not allowed to update kitchen id via this route"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = RestaurantSerializer(restaurant_profile, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Http method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def update_restaurant_balance(request):

    data = request.data

    user = request.user

    # Check if user is a restaurant
    try:
        user = User.objects.get(id=user.id)
    except User.DoesNotExist:
        return Response({"message": "User was not found"}, status=status.HTTP_404_NOT_FOUND)
    # User must be a chef
    if user.role != "chef":
        return Response({"message": "User must be a chef. Permission denied."}, status=status.HTTP_401_UNAUTHORIZED)

    restaurant_profile = Restaurant.objects.filter(user=user).first()

    amount = data.get("amount")

    # Check if amount was given
    if not amount:
        return Response({"message": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if amount is an integer
    if not isinstance(amount, int):
        return Response({"message": "amount must be an integer"}, status=status.HTTP_400_BAD_REQUEST)


    old_balance = restaurant_profile.balance
    new_balance = old_balance - amount


    if new_balance >= 0:
        restaurant_profile.balance = new_balance
        restaurant_profile.save()
        return Response({"message": "Balance has been updated successfully!", "current_balance": restaurant_profile.balance}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "amount is greater than current balance", "current_balance": restaurant_profile.balance}, status=status.HTTP_400_BAD_REQUEST)



    













# DRIVER PROFILE
@api_view(['PUT', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def get_driver_profile(request):
    # Get User object
    # The case of user not existing given the token is highly unlikely
    # but additional checks must be made
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"message": "User was not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # User must be a driver
    if user.role != "logistics":
        return Response({"message": "User must be a driver"}, status=status.HTTP_404_NOT_FOUND)

    user_profile = UserProfile.objects.filter(user=user).first()
    driver_profile = Driver.objects.filter(user=user).first()

    if request.method == 'GET':
        serializer = DriverSerializer(driver_profile)
        driver_details = {
            "id": serializer.data.get("id"),
            "restaurant_id": serializer.data.get("restaurant"),
            "vehicle_color": serializer.data.get("vehicle_color"),
            "vehicle_description": serializer.data.get("vehicle_description"),
            "vehicle_number": serializer.data.get("vehicle_number"),
            "available": serializer.data.get("available"),
            "profile_details": serializer.data.get("profile_details"),
            "vehicle_image_url": serializer.data.get("vehicle_image_url"),
            "permissions": {
                "is_superuser": user.is_superuser,
                "is_driver": user.role == "logistics",
                "is_restaurant": user.role == "chef",
                "is_customer": user.role == "customer"
            }
        }
        return Response(driver_details, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        data = request.data
        # name, description, image, address
        if data.get("driver_id"):
            return Response({
                "message":"You are not allowed to update driver id via this route"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = DriverSerializer(driver_profile, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    return Response({"message": "This is the driver's profile"}, status=status.HTTP_200_OK)


# DRIVER AUTH VIEWS
@api_view(['POST'])
def login_driver(request):
    data = request.data
    driver_id = data.get("driver_id")
    password = data.get("password")

    if not driver_id:
        return Response({"message": "driver_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({"message": "password is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Search if the driver exists in either the Driver or User models
    try:
        user = User.objects.filter(username=driver_id).first()
    except User.DoesNotExist:
        user = None
        return Response({"message": "user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        driver = Driver.objects.filter(driver_id=driver_id).first()
    except Driver.DoesNotExist:
        driver = None
        return Response({"message": "driver does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user:
        return Response({"message": "User does not exist. "}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.is_verified:
        return Response({"message": "User is not verified"}, status=status.HTTP_401_UNAUTHORIZED)
    
    if user and driver:
        # If both a user and a driver were found for that username/ID, check passwords
        if user.check_password(password):
            return Response({
                "token": user.auth_token.key, 
                "user_id": user.id, 
                "driver_id": user.username, 
                "email": user.email,
                "permissions": {
                    "is_superuser": user.is_superuser,
                    "is_driver": user.role == "logistics",
                    "is_restaurant": user.role == "chef",
                    "is_customer": user.role == "customer"
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "user with driver id does exists"}, status=status.HTTP_400_BAD_REQUEST)

# Get Driver profile


# This api view should only be assessed by restaurants (kitchens) and admin
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated & (IsAdminUser | IsRestaurantUser)])
def create_driver(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")
    vehicle_color = data.get("vehicle_color")
    vehicle_description = data.get("vehicle_description")
    vehicle_number = data.get("vehicle_number")
    vehicle_image_url = data.get("vehicle_image_url")
    available = data.get("available", False)
    

    # Create driver user
    # Check if user already exists
    # If user exists, do not create user

    if not email:
        return Response({
            "email": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    elif not password:
        return Response({
            "password": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    elif not vehicle_color:
        return Response({
            "vehicle_color": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    elif not vehicle_description:
        return Response({
            "vehicle_description": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    elif not vehicle_number:
        return Response({
            "vehicle_number": [
                "This field may not be blank."
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        # Check if email and password are valid entry
        email_valid_status = check_email(email)
        password_valid_status = is_valid_password(password)
        if email_valid_status.status == False:
            return Response({
                "email": [
                    error_message for error_message in email_valid_status.error_messages
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password_valid_status.status == False:
            return Response({
                "password": [
                    error_message for error_message in password_valid_status.error_messages
                ]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Lastly Check if user already exists
        existing_user = User.objects.filter(email=email)
        if len(existing_user) > 1 or existing_user:
            return Response({
                "email": [
                    "User with email already exists."
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Finally create user Create user
            if request.user.role != "chef":
                return Response({
                    "detail": "only restaurants have permission to add drivers"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            code = generate_4_digit_code()
            data.update({"role": "logistics", "code": code})
            serializer = serializers.UserSerializer(data=data)
            if serializer.is_valid():
                created_user = serializer.save()
                # if request.user.role == "chef":
                # Query for the user restaurant model if user is chef
                restaurant = Restaurant.objects.filter(user=request.user).first()
                # Get the Driver
                driver = Driver.objects.filter(user=created_user).first()
                # Assign the driver to the restaurant
                driver.restaurant = restaurant
                driver.vehicle_color = vehicle_color
                driver.vehicle_description = vehicle_description
                driver.vehicle_number = vehicle_number
                driver.vehicle_image_url = vehicle_image_url
                driver.available = available
                driver.save()
                # Object / Dictionary to be returned after user has been created
                user_details = {
                    "message": f"A verification code has been sent to {serializer.data.get('email')}.",
                    "user_id": serializer.data.get("id"),
                    "driver_id": driver.driver_id,
                    "role": serializer.data.get("role"),
                }
                response_gotten_from_code = send_registration_code_mail(code, serializer.data.get('email'))
                return Response(user_details, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated & IsUserDriver])
def driver_analytics(request):
    # Check if the user accessing this route is a driver
    # If true, send the driver analytics to the client
    # Else return a message user does not have the permission
    if request.user.role != "logistics":
        return Response({"messge": "User must be a driver"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        driver = Driver.objects.get(user=request.user)
        ordereditems = OrderItem.objects.filter(driver=driver)

        # Get the pending runs and the successful runs
        orderitems_completed = ordereditems.filter(status="completed")
        orderitems_pending = ordereditems.filter(status="pending")
        orderitems_cancelled = ordereditems.filter(status="cancelled")

        reviews = driver.driver_rated.all()

        print("driver: ", driver)
        print("orderitems by driver: ", ordereditems)
    except Restaurant.DoesNotExist:
        return Response({"message": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    analytics = {
            "completed_orders_count": orderitems_completed.count(),
            "pending_orders_count": orderitems_pending.count(),
            "cancelled_orders_count": orderitems_cancelled.count(),
            "total_orders": ordereditems.count(),
            "reviews": {
                "driver_ratings": driver.ratings,
                "reviews_count": reviews.count(),
            },
    }

    return Response({"message": "Here's your analytics", "analytics": analytics}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated & IsRestaurantUser])
def restaurant_analytics(request):
    # Check if the user accessing this route is a restaurant
    # If true, send the driver analytics to the client
    # Else return a message user does not have the permission
    if request.user.role != "chef":
        return Response({"messge": "User must be a restaurant or chef"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        restaurant = Restaurant.objects.get(user=request.user)
        ordereditems = OrderItem.objects.filter(restaurant=restaurant)

        completed_orders_count = ordereditems.filter(status="completed").count()
        pending_orders_count = ordereditems.filter(status="pending").count()
        cancelled_orders_count = ordereditems.filter(status="cancelled").count()
        total_orders = ordereditems.count()

        reviews = restaurant.restaurant_rated.all()


        analytics = {
            "completed_orders_count": completed_orders_count,
            "pending_orders_count": pending_orders_count,
            "cancelled_orders_count": cancelled_orders_count,
            "total_orders": total_orders,
            "reviews": {
                "restaurant_ratings": restaurant.ratings,
                "reviews_count": reviews.count(),
            },
            "num_available_drivers": restaurant.driver_set.all().count(),
            "total_revenue": restaurant.balance
        }

    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"message": "Here's your analytics", "analytics": analytics}, status=status.HTTP_200_OK)



# Restaurant Withdrawal view

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def retaurant_withdrawal_list_view(request):

    user = request.user
    if user.role != "chef":
        return Response({"messge": "User must be a restaurant or chef"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if the user has a restaurant object
    try:
        restaurant = Restaurant.objects.get(user=user)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exists."}, status=status.HTTP_404_NOT_FOUND)
    

    if request.method == 'GET':
        restaurant_withdrawals = RestaurantWithdrawal.objects.filter(user=user)
        serializer = RestaurantWithdrawalSerializer(restaurant_withdrawals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        
        data = request.data

        res = {
            "user": user.id,
            **data
        }

        serializer = RestaurantWithdrawalSerializer(data=res)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Http method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def retaurant_withdrawal_detail_view(request, pk):
    
    user = request.user

    if request.user.role != "chef":
        return Response({"messge": "User must be a restaurant or chef"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        restaurant_withdrawal = RestaurantWithdrawal.objects.get(user=user, pk=pk)
    except RestaurantWithdrawal.DoesNotExist:
        return Response({"message": "Restaurant Withdrawal does not exists."})
    
    if request.method == 'GET':
        serializer = RestaurantWithdrawalSerializer(restaurant_withdrawal)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        data = request.data
        serializer = RestaurantWithdrawalSerializer(restaurant_withdrawal, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        restaurant_withdrawal.delete()
        return Response({"message": "Restaurant withdrawal history deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    return Response({"message": "Http method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





