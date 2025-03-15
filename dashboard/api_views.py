from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django.contrib.auth import authenticate, login

from authentication.models import User as CustomUser


from django.contrib import messages

from app.models import Restaurant

from .constants import upload_to_cloudinary


from authentication.helpers import (
    check_email, 
    is_valid_password, 
    generate_4_digit_code, 
    send_registration_code_mail, 
    check_if_code_matches,
)


@api_view(['POST'])
def dashboard_login_api(request):
    data = request.data
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = CustomUser.objects.get(email=email)
        user = authenticate(request, email=user.email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # Change the redirect url here if you change the dashboard
            return Response({'message': 'Login successful', 'redirect_url': '/dashboard'}, status=status.HTTP_200_OK)
        else:
            messages.success(request, "Invalid credentials")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


    

@api_view(['POST'])
def dashboard_register_api(request):
    data = request.data

    
    print(data)
    # Check if user already exist


    if request.method == 'POST':

        data = request.data

        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("password_confirmation")

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        phone_number = data.get("phone_number")
        bio = data.get("bio")
        country = data.get("country")
        postal_code = data.get("postal_code")
        state = data.get("state")
        role = data.get("role", "chef")
        date_of_birth = data.get("date_of_birth")

        if not email:
            return Response({
                "message": 
                    "Email field may not be blank.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not password:
            return Response({
                "message": 
                    "Password field may not be blank.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not confirm_password:
            return Response({
                "message": 
                    "Confirm Password field may not be blank.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif confirm_password != password:
            return Response({
                "message": 
                    "Both password must match.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            # Check if email and password are valid entry
            email_valid_status = check_email(email)
            password_valid_status = is_valid_password(password)
            if email_valid_status.status == False:
                return Response({
                    "message": "".join([error_message for error_message in email_valid_status.error_messages]),
                    "success": False,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if password_valid_status.status == False:
                return Response({
                    "message":
                        "".join([error_message for error_message in password_valid_status.error_messages]),
                        "success": False,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Lastly Check if user already exists
            existing_user = CustomUser.objects.filter(email=email)
            if len(existing_user) > 1 or existing_user:
                return Response({
                    "message":"User with email already exists.",
                    "success": False,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:

                
                # Finally create user Create user
                code = generate_4_digit_code()

                user = CustomUser(
                    username=username,
                    email=email,
                    role=role,
                    provider="email",
                    code=code,
                )

                user.set_password(password)

                user.save()

                user.profile.name = f"{first_name} {last_name}"
                user.profile.date_of_birth = date_of_birth
                user.profile.phone_number = phone_number
                user.profile.bio = bio
                user.profile.country = country
                user.profile.state = state
                user.profile.postal_code = postal_code


                user.profile.save()
                user.save()

                return Response({"message": "User created successfully. You may log in.", "success": True}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def restaurant_edit_api(request, pk):
    data = request.data
    
    postal_code = data.get("postal_code")
    country = data.get("country")
    state = data.get("state")
    phone_number = data.get("phone_number")

    restaurant_name = data.get("name")
    description = data.get("description")
    restaurant_address = data.get("restaurant_address")
    restaurant_image = request.FILES.get("restaurant_image", None)

    try:
        restaurant = Restaurant.objects.get(id=pk)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant Does not exist.", "success": False}, status=status.HTTP_404_NOT_FOUND)
    
    # restaurant.user.profile.name = 


    # Upload image to Cloudinary
    image_url = upload_to_cloudinary(restaurant_image) if restaurant_image else None
    print("Cloudinary Secured URL: ", image_url)
    if image_url:
        restaurant.image_url = image_url
    restaurant.name = restaurant_name
    restaurant.description = description
    restaurant.address = restaurant_address
    restaurant.user.profile.state = state
    restaurant.user.profile.country = country
    restaurant.user.profile.phone_number = phone_number
    restaurant.user.profile.postal_code = postal_code

    restaurant.user.profile.save()

    restaurant.save()

    print(data)
    return Response({"message": "Restaurant Updated Successfully!", "success": True}, status=status.HTTP_200_OK)



@api_view(['POST'])
def restaurant_create_api(request):
    # Create a new user that is a restaurant
    
    return Response({"message": "Restaurant Created Successfully!", "success": True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def users_create_api(request):

    if request.method == "POST":
        data = request.data
        email = data.get("email")
        role = data.get("role")
        password = data.get("password")
        confirm_password = data.get("re_password")

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        phone_number = data.get("phone_number")
        profile_image = request.FILES.get("profile_image")
        bio = data.get("bio")
        country = data.get("country")
        postal_code = data.get("postal_code")
        state = data.get("state")
        role = data.get("role", "chef")
        date_of_birth = data.get("date_of_birth")


        if not email:
            return Response({
                "message": 
                    "Email field may not be blank.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not password:
            return Response({
                "message": 
                    "Password field may not be blank.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not confirm_password:
            return Response({
                "message": 
                    "Confirm Password field may not be blank.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        elif confirm_password != password:
            return Response({
                "message": 
                    "Both password must match.",
                    "success": False,
                
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Check if email and password are valid entry
            email_valid_status = check_email(email)
            password_valid_status = is_valid_password(password)
            if email_valid_status.status == False:
                return Response({
                    "message": "".join([error_message for error_message in email_valid_status.error_messages]),
                    "success": False,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if password_valid_status.status == False:
                return Response({
                    "message":
                        "".join([error_message for error_message in password_valid_status.error_messages]),
                        "success": False,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            

            # Lastly Check if user already exists
            existing_user = CustomUser.objects.filter(email=email)
            if len(existing_user) > 1 or existing_user:
                return Response({
                    "message":"User with email already exists.",
                    "success": False,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:

                image_url = upload_to_cloudinary(profile_image)
                # Finally create user Create user
                code = generate_4_digit_code()

                user = CustomUser(
                    email=email,
                    role=role,
                    provider="email",
                    code=code,
                )

                user.set_password(password)

                user.save()

                user.profile.name = f"{first_name} {last_name}"
                user.profile.date_of_birth = date_of_birth
                user.profile.phone_number = phone_number
                user.profile.bio = bio
                user.profile.country = country
                user.profile.state = state
                user.profile.postal_code = postal_code
                user.profile.image_url = image_url

                user.profile.save()
                user.save()

        print("The data from client: ", request.data)
        return Response({"message": "User Created Successfully!", "success": True}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Method not allowed", "success": False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['PUT'])
def user_update_api(request, pk):
    data = request.data

    try:
        user = CustomUser.objects.get(id=pk)
    except CustomUser.DoesNotExist:
        return Response({"message": "User does not exist", "success": False}, status=status.HTTP_404_NOT_FOUND)

    first_name = data.get("first_name", user.profile.first_name)
    last_name = data.get("last_name", user.profile.last_name)
    phone_number = data.get("phone_number", user.profile.phone_number)
    profile_image = request.FILES.get("profile_image")
    bio = data.get("bio", user.profile.bio)
    country = data.get("country", user.profile.country)
    postal_code = data.get("postal_code", user.profile.postal_code)
    state = data.get("state", user.profile.state)
    date_of_birth = data.get("date_of_birth", user.profile.date_of_birth)

    # Prevent password update
    if "password" in data or "re_password" in data:
        return Response({
            "message": "Password update is not allowed in this endpoint.",
            "success": False,
        }, status=status.HTTP_400_BAD_REQUEST)

    # Update user profile
    user.profile.first_name = first_name
    user.profile.last_name = last_name
    user.profile.phone_number = phone_number
    user.profile.bio = bio
    user.profile.country = country
    user.profile.state = state
    user.profile.postal_code = postal_code
    user.profile.date_of_birth = date_of_birth

    if profile_image:
        image_url = upload_to_cloudinary(profile_image)
        user.profile.image_url = image_url

    user.profile.save()
    user.save()

    return Response({"message": "User Updated Successfully!", "success": True}, status=status.HTTP_200_OK)


