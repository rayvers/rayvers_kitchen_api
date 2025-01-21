from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import parsers, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from .serializers import (
    CustomAuthTokenSerializer, 
    UserProfileSerializer, 
    UserSerializer, 
    UserAddressSerializer,
)

from app.permissions import (
    IsUserVerified
)

from app.models import (
    Restaurant,
    Driver
)

from .models import (
    UserProfile, 
    UserAddress,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth import get_user_model

# from asgiref.sync import sync_to_async
import requests

from .helpers import (
    check_email, 
    is_valid_password, 
    generate_4_digit_code, 
    send_registration_code_mail, 
    check_if_code_matches,
)



User = get_user_model()


# ------------------------------- Home views -----------------------------------
class HomeAPIAuthViewList(APIView):
    def get(self, request):
        return Response({"message": "Welcome to Reyvers Kitchen Auth service API"})



# async_send_registration_code_mail = sync_to_async(send_registration_code_mail_async)

# CREATE NEW USER
@api_view(['POST'])
def create_new_user(request):
    if request.method == 'POST':
        email = request.data.get("email")
        password = request.data.get("password")
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
                data = request.data
                code = generate_4_digit_code()
                data.update({"code": code})
                serializer = UserSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    user_details = {
                        "message": f"A verification code has been sent to {serializer.data.get('email')}.",
                        "user_id": serializer.data.get("id"),
                        "email": serializer.data.get("email"),
                        "role": serializer.data.get("role"),
                    }
                    
                    response_gotten_from_code = send_registration_code_mail(code, user_details["email"])
                    # print("The response status I got from the code registration: ", response_gotten_from_code)

                    return Response(user_details, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({ "detail": "Http method not allowed." }, status=status.HTTP_405_METHOD_NOT_ALLOWED)



# Verify user registration
@api_view(['POST'])
def verify_user_upon_registration(request):
    """Verifies a user upon registration using the provided code"""
    data = request.data
    code = data.get("code")
    user_id = data.get("user_id")

    # Check if user exists in database
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # print("something wrong occurred --- User does not exist.")
        return Response({"message": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        is_correct_code = check_if_code_matches(user.code, code)
        if is_correct_code:
            user.is_verified = True
            user.code = None
            user.save()
            return Response({
                "message": "Account has been verified successfully. Proceed to login.",
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User code is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except AssertionError:
        # print("Values must be valid integers")
        return Response({"message": "Values must be valid integers"}, status=status.HTTP_400_BAD_REQUEST)

# Retry Verify user registration
@api_view(['POST'])
def verify_user_retry_code(request):
    """
    Resend verification code to user mail
    All that is needed to perform this task is the user_id
    """
    data = request.data
    user_id = data.get("user_id")
    # Generate and send new profile code
    code_generated = generate_4_digit_code()

    # Check if user exists
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # print("User does not exist.")
        return Response({"message": "Invalid user id. User does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Send some code to user email
    user.code = code_generated
    user.save()

    response_gotten_from_code = send_registration_code_mail(code_generated, user.email)
    if response_gotten_from_code == 200:
        return Response({"message": "Code was resent to your email"}, status=status.HTTP_200_OK)
    else:
        # Here the status code could be any respond coming from email backend
        return Response({"message": "Encountered an issue sending email. Retry!"}, status=response_gotten_from_code)
    

    
# Forget Password view
@api_view(['POST'])
def forget_password_view_email(request):
    """
    This view sends password reset code to user's email
    
    """
    # Get user email
    data = request.data
    email = data.get("email")
    code_generated = generate_4_digit_code()
    # Check if user with email exists in the database
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "User with email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set the code in the user email
    user.code = code_generated
    user.save()

    # Here we should sent a verification code to user for confirmation of their identity
    # Send code verification to provided email
    response_gotten_from_code = send_registration_code_mail(code_generated, email)

    # Return a response
    if response_gotten_from_code == 200:
        return Response({"message": "Code was sent to your email", "user_id": user.id}, status=status.HTTP_200_OK)
    else:
        # Here the status code could be any respond coming from email backend
        return Response({"message": "Encountered an issue sending email. Retry!", "user_id": user.id}, status=response_gotten_from_code)
    

@api_view(['POST'])
def forget_password_view_code(request):
    """
    Verifies that the code the user received in their email is correct
    @params: code, user_id, password, re_password
    """
    data = request.data
    entered_code = data.get("code")
    user_id = data.get("user_id")

    # Password
    password = data.get("password")
    re_password = data.get("re_password")

    if not entered_code:
        return Response({"message": "Please enter the code sent to your mail."}, status=status.HTTP_400_BAD_REQUEST)

    if not user_id:
        return Response({"message": "Unidentified user. Please send the user_id in payload."}, status=status.HTTP_401_UNAUTHORIZED)

    if not password:
        return Response({"password": ["Password is required"]}, status=status.HTTP_400_BAD_REQUEST)
    if not re_password:
        return Response({"password": ["Password Confirmation is required"]}, status=status.HTTP_400_BAD_REQUEST)
    
    if not all([password, re_password]):
        return Response({
            "password": ["Please enter your password for both fields: password and re_password"]
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if both password and re_password are valid strings
    if not all([str(password) == password, str(re_password) == re_password]):
        return Response({"password": ["Passwords must be valid strings"]}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if password and re_password are a match
    if password != re_password:
        return Response({"password": ["Passwords do not match"]}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if passwords meet the django validation score
    password_valid_status = is_valid_password(password)
    if password_valid_status.status == False:
        return Response({
            "password": [
                error_message for error_message in password_valid_status.error_messages
            ]
        }, status=status.HTTP_400_BAD_REQUEST)


    # Check if user exists
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    if user.code == None:
        return Response({"message": "Code is invalid"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user has code and the code is correct
    if not int(user.code) == int(entered_code):
        return Response({"message": "Code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if user.check_password(password):
            return Response({"message": "Current password must not be same as previous password"}, status=status.HTTP_400_BAD_REQUEST)
        # Change the user code so it can't be used again
        user.set_password(password)
        user.code = None
        user.save()
        # Check if password is good
        return Response({"message": "Password was reset successfully."}, status=status.HTTP_200_OK)

    


# LOGIN USER
class CustomAuthToken(APIView):
    throttle_classes = []
    permission_classes = []
    parser_classes = [parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser]
    renderer_classes = [renderers.JSONRenderer]
    serializer_class = CustomAuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }
    
    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_verified:
            return Response({"message": "User is not verified"}, status=status.HTTP_401_UNAUTHORIZED)
        # Change user token once requests are made continually
        oldTokens = Token.objects.filter(user__id=user.id)
        for token in oldTokens:
            token.delete()

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            "permissions": {
                "is_superuser": user.is_superuser,
                "is_driver": user.role == "logistics",
                "is_restaurant": user.role == "chef",
                "is_customer": user.role == "customer"
            }
        })

# USER LOGOUT VIEW
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def logoutView(request):
    user = request.user
    # Check if the Authorization header is present in the request

    if 'Authorization' in request.headers:
        # Extract the token from the Authorization header
        auth_header = request.headers['Authorization']
        _, token = auth_header.split()  # Assuming the token is separated by a space after "Token"
        
        # Check if the token exists in the database
        try:
            user_token = Token.objects.get(key=token)
            user_token.delete()
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



def get_user_from_token(request):
    # Check if the Authorization header is present in the request
    if 'Authorization' in request.headers:
        # Extract the token from the Authorization header
        auth_header = request.headers['Authorization']
        _, token = auth_header.split()  # Assuming the token is separated by a space after "Token"
        if token:
            token = Token.objects.get(key=token)
            return token.user
        else:
            return None
    else:
        return None


# USER PROFILE
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
@parser_classes([MultiPartParser, FormParser])
def get_current_user_profile(request):
    if request.method == 'GET':
        user = get_user_from_token(request)
        if user:
            userData = {
                "id": user.id,
                "email": user.email,
                "name": user.profile.name,
                "date_of_birth": user.profile.date_of_birth,
                "profile_picture": user.profile.get_image_url,
                "bio": user.profile.bio,
                "role": user.role,
                "image_url": user.profile.image_url,
                "permissions": {
                    "is_superuser": user.is_superuser,
                    "is_driver": user.role == "logistics",
                    "is_restaurant": user.role == "chef",
                    "is_customer": user.role == "customer"
                }
            }
            return Response(userData, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Authorization header not found in the request."}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        uploaded_file = request.FILES.get('profile_image')
        # print("This is the file upload: ", uploaded_file)
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profile was not  found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({"message": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                                


# Current user address view
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def current_user_address_view(request):
    if request.method == 'GET':
        user_addresses = UserAddress.objects.filter(user=request.user)
        
        serializer = UserAddressSerializer(user_addresses, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'POST': 
        
        user_address_exists = UserAddress.objects.filter(
            user=request.user, 
            labelled_place=request.data.get("labelled_place")
        )
        if len(user_address_exists) > 0:
            return Response({"detail": "Labelled place already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_address_details = {
            "user": request.user.id,
            "address": request.data.get("address", None),
            "street": request.data.get("street", None),
            "post_code": request.data.get("post_code", None),
            "apartment": request.data.get("apartment", None),
            "labelled_place": request.data.get("labelled_place", None),
        }
        serializer = UserAddressSerializer(data=user_address_details)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)

    return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def detail_user_address_view(request, pk):
    if request.method == 'GET':
        try:
            user_address = UserAddress.objects.get(pk=pk)
            serializer = UserAddressSerializer(user_address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserAddress.DoesNotExist:
            return Response({"detail": "user address not found"}, status=status.HTTP_404_NOT_FOUND)
        
    elif request.method == 'PUT':
        # Check if the requesting user is the owner of the address
        user_address = UserAddress.objects.get(pk=pk)
        user_address_data = {
            "id": user_address.id,
            "user": request.user.id,
            "address": request.data.get("address"),
            "street": request.data.get("street"),
            "post_code": request.data.get("post_code"),
            "apartment": request.data.get("apartment"),
            "labelled_place": user_address.labelled_place
        }
        if user_address.labelled_place != request.data.get("labelled_place"):
            return Response({"detail": "Label must match"}, status=status.HTTP_400_BAD_REQUEST)
        if user_address.user != request.user:
            return Response({"detail": "User does not have permission to edit content"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = UserAddressSerializer(instance=user_address, data=user_address_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        # Check if the requesting user is the owner of the address
        try:
            user_address = UserAddress.objects.get(pk=pk)
            if user_address.user != request.user:
                return Response({"detail": "User does not have permission to delete content"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_address.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
        except UserAddress.DoesNotExist:
            return Response({"detail": "user address not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def change_user_password(request):
    data = request.data
    
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirm_new_password = data.get("confirm_new_password")


    # Check if both fields are provided
    if not all([old_password, new_password, confirm_new_password]):
        return Response({"password": ["old_password, new_password and confirm_new_password fields are required."]}, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != confirm_new_password:
        return Response({"password": ["Passwords do not match."]}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user exists
    # It is highly unlikely that user does not
    # exist given the token
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"password": ["Invalid user credentials. User does not exist."]}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if old_passwordd and new_password are a match
    if old_password == new_password:
        return Response({"password": ["New password must be different from the previous passwords. "]}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if old_password field is correct or wrong
    if not user.check_password(old_password):
        return Response({"password": ["Old Password entered is incorrect"]}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if passwords meet the django validation score
    password_valid_status = is_valid_password(new_password)
    if password_valid_status.status == False:
        return Response({
            "password": [
                error_message for error_message in password_valid_status.error_messages
            ]
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Finally update password
    user.set_password(new_password)
    user.save()
    return Response({"message": "Password was successfully updated."}, status=status.HTTP_200_OK)
    


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def change_user_username(request):
    # Get username
    username =  request.data.get("username")

    if not username:
        return Response({"username": ["username field is required."]}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a check to see if username already exists in the database
    user_existing_in_db = User.objects.filter(username=username).exclude(id=request.user.id)
    if len(user_existing_in_db) > 0:
        return Response({"username": ["A user with username already exists. "]}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user exists
    # It is highly unlikely that user does not
    # exist given the token
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"username": ["User does not exist."]}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is a chef (restaurant)
    # If they are, the restaurant table should be updated as well as the user table

    if user.role == "chef":
        restaurant = Restaurant.objects.filter(user=user).first()
        if restaurant:
            # Update both table with same data
            user.username = username
            user.save()
            restaurant.kitchen_id = username
            restaurant.save()

        else:
            pass

    elif user.role == "logistics":
        driver = Driver.objects.filter(user=user).first()
        if driver:
            # Update both table with same data
            user.username = username
            user.save()
            driver.driver_id = username
            driver.save()
        else:
            pass
    else:
        user.username = username
        user.save()

    return Response({"message": "Username was successfully updated."}, status=status.HTTP_200_OK)








