from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model


from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .permissions import (
    IsUserChef,
    IsUserCustomer,
    IsUserDriver,
    IsUserVerified,
)


from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from . import serializers
from .import models


UserModel = get_user_model()

# Create your views here.

# Custom Paginator class
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ------------------------------- Home views -----------------------------------
class HomeAPIViewList(APIView):
    def get(self, request):
        return Response({"message": "Welcome to Reyvers Kitchen API"})
    

# ------------------------------- Category views -----------------------------------
class CategoryViewList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    serializer_class =  serializers.CategorySerializer
    pagination_class = CustomPageNumberPagination
    

    def get(self, *args, **kwargs):
        """Returns a list of all categories"""
        categories = models.Category.objects.all().order_by("-pk")
        paginator = CustomPageNumberPagination()

        # Use the pagination class to paginate the queryset
        paginated_categories = paginator.paginate_queryset(categories, self.request)

        serializer = self.serializer_class(paginated_categories, many=True)
        
        return Response({
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        })
        

    def post(self, *args, **kwargs):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CategoryViewDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    serializer_class =  serializers.CategorySerializer
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, *args, **kwargs):
        """Returns a category detail and paginated dishes under the category"""
        pk = kwargs["pk"]
        category = get_object_or_404(models.Category, pk=pk)
        serializer = self.serializer_class(category)

        # Get all the dishes under this category
        dishes = models.Dish.objects.filter(category__id=pk).order_by("-pk")

        # Serialize the dishes
        dishes_serializer = serializers.DishSerializer(dishes, many=True)

        context = {
            "id": serializer.data.get("id"),
            "name": serializer.data.get("name"),
            "image_url": serializer.data.get("image_url"),
            "dishes": dishes_serializer.data,
        }

        return Response(context, status=status.HTTP_200_OK)

    def put(self, *args, **kwargs):
        pk = kwargs["pk"]
        category = get_object_or_404(models.Category, pk=pk)
        serializer = self.serializer_class(category, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, *args, **kwargs ):
        pk = kwargs["pk"]
        print("The category details view was called")
        try:
            category = models.Category.objects.get(pk=pk)
            category.delete()
            return Response({"details": "category has been deleted successfully "}, status=status.HTTP_204_NO_CONTENT)
        except models.Category.DoesNotExist:
            return Response({"details": "category with id not found"}, status=status.HTTP_404_NOT_FOUND)



# ------------------------------- Ingredient views -----------------------------------
class IngredientViewList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.IngredientSerializer

    def get(self, *args, **kwargs ):
        """Returns a list of all INGREDIENTS"""
        ingredients = models.Ingredient.objects.all().order_by("-pk")

        paginator = CustomPageNumberPagination()

        paginated_ingredient = paginator.paginate_queryset(ingredients, self.request)

        serializer = self.serializer_class(paginated_ingredient, many=True)

    
        return Response({
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        })
    
    def post(self, *args, **kwargs):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class IngredientDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.IngredientSerializer

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            ingredient = models.Ingredient.objects.get(pk=pk)
            serializer = serializers.IngredientSerializer(ingredient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Ingredient.DoesNotExist:
            return Response({"details": "ingredient with id not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, *args, **kwargs):
        pk = kwargs["pk"]
        ingredient = get_object_or_404(models.Ingredient, pk=pk)
        serializer = self.serializer_class(ingredient, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, *args, **kwargs ):
        pk = kwargs["pk"]
        try:
            ingredient = models.Ingredient.objects.get(pk=pk)
            ingredient.delete()
            return Response({"details": "Ingredient has been deleted successfully "}, status=status.HTTP_204_NO_CONTENT)
        except models.Ingredient.DoesNotExist:
            return Response({"details": "Ingredient with id not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------------------- Dish views -----------------------------------
class DishesViewList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.DishSerializer

    pagination_class = CustomPageNumberPagination

    def get(self, *args, **kwargs ):
        """Returns a list of all dishes"""
        dishes = models.Dish.objects.all().order_by("-pk")

        paginator = CustomPageNumberPagination()

        paginated_dishes = paginator.paginate_queryset(dishes, self.request)

        serializer = self.serializer_class(paginated_dishes, many=True)

        # print(serializer.data)
    
        return Response({
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        })

        

        

    def post(self, *args, **kwargs ):
        data = self.request.data

        ingredients = data.get("ingredients")
        # print("INGREDIENTS: ", ingredients)

        
        # Ensure only chef that added dishes can delete them
        requesting_user_chef_id = self.request.user.id
        # Get the chef models to see if the requesting user is a chef
        try:
            chef = models.Restaurant.objects.get(user=self.request.user)
            # print(chef.id)
        except:
            return Response({"message": "You must be logged in as a chef to add dishes"}, status=status.HTTP_401_UNAUTHORIZED)

        if self.request.user.role == "chef":
            if requesting_user_chef_id == chef.user.id:
                serializer = self.serializer_class(data=data, context={'request': self.request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                # return Response({"message": "Yes"})
            else:
                return Response({"details": "You do not have permission to add dishes"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"details": "Only chefs can add dishes"}, status=status.HTTP_401_UNAUTHORIZED)










class DishDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.DishSerializer

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            dish = models.Dish.objects.get(pk=pk)
            serializer = serializers.DishSerializer(dish)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Dish.DoesNotExist:
            return Response({"details": "dish with id not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, *args, **kwargs):
        pk = kwargs["pk"]
        dish = get_object_or_404(models.Dish, pk=pk)
        serializer = self.serializer_class(dish, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            dish = models.Dish.objects.get(pk=pk)
            dish.delete()
            return Response({"details": "dish has been deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except models.Dish.DoesNotExist:
            return Response({"details": "dish with id not found"}, status=status.HTTP_404_NOT_FOUND)


class DishDetailRatingView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            dish = models.Dish.objects.get(pk=pk)
        except models.Dish.DoesNotExist:
            return Response({
                "message": "dish with id not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the cusumer rating is permitted to 
        # be displayed in the app or approved by the admin

        ratings = models.DishRating.objects.filter(dish=dish, approved=True)

        serializer = serializers.DishRatingSerializer(ratings, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)




    def post(self, *args, **kwargs):
        # Get the dish id we are rating
        pk = kwargs["pk"]
        try:
            dish = models.Dish.objects.get(pk=pk)
        except models.Dish.DoesNotExist:
            return Response({
                "message": "dish with id not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # We get the two accepted data in our payload which are:
        # - rating_number (rating_number must be from 1 - 5)
        # - user (user will be derived from the request user object)

        user = self.request.user
        rating_number = self.request.data.get("rating_number")
        rating_text = self.request.data.get("rating_text")

        if not rating_number:
            return Response({"message": "rating_number is required"}, status=status.HTTP_400_BAD_REQUEST)
        

        if not isinstance(rating_number, int):
            return Response({"message": "rating_number must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        if int(rating_number) > 5 or int(rating_number) < 1:
            return Response({"message": "rating_number must be between 1 - 5"}, status=status.HTTP_400_BAD_REQUEST)

        

        # Check if the user and dish is already in the rating table
        # If it is, don't create a new one instead 
        # If not, create a new one in the database
        try:
            user_ratings_for_dish = models.DishRating.objects.get(user=user, dish=dish)
            rating = user_ratings_for_dish
            rating.number = rating_number
            if rating_text:
                rating.text = rating_text
            rating.save()
            return Response({"message": "User rating was successfully updated"}, status=status.HTTP_200_OK)
        except models.DishRating.DoesNotExist:
            dish_rating = models.DishRating.objects.create(user=user, dish=dish, number=rating_number)
            if rating_text:
                dish_rating.text = rating_text
                dish_rating.save()
            return Response({"message": "User rating was successfully added"}, status=status.HTTP_200_OK)

class RestaurantDetailRating(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            restaurant = models.Restaurant.objects.get(pk=pk)
        except models.Restaurant.DoesNotExist:
            return Response({
                "message": "restaurant with id not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the cusumer rating is permitted to 
        # be displayed in the app or approved by the admin

        ratings = models.RestaurantRating.objects.filter(restaurant=restaurant, approved=True)

        serializer = serializers.RestaurantRatingSerializer(ratings, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        # Get the dish id we are rating
        pk = kwargs["pk"]
        try:
            restaurant = models.Restaurant.objects.get(pk=pk)
        except models.Restaurant.DoesNotExist:
            return Response({"details": "restaurant with id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # We get the two accepted data in our payload which are:
        # - rating_number (rating_number must be from 1 - 5)
        # - user (user will be derived from the request user object)

        user = self.request.user
        rating_number = self.request.data.get("rating_number")
        rating_text = self.request.data.get("rating_text")

        if not isinstance(rating_number, int):
            return Response({"message": "rating_number must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        if int(rating_number) > 5 or int(rating_number) < 0:
            return Response({"message": "rating_number must be between 1 - 5"}, status=status.HTTP_400_BAD_REQUEST)

        if not rating_number:
            return Response({"message": "rating_number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_ratings_for_restaurant = models.RestaurantRating.objects.get(user=user, restaurant=restaurant)
            rating = user_ratings_for_restaurant
            rating.number = rating_number
            if rating_text:
                rating.text = rating_text
            rating.save()
            return Response({"message": "User rating was successfully updated"}, status=status.HTTP_200_OK)
        except models.RestaurantRating.DoesNotExist:
            user_ratings_for_restaurant = models.RestaurantRating.objects.create(user=user, restaurant=restaurant, number=rating_number)
            if rating_text:
                user_ratings_for_restaurant.text = rating_text
                user_ratings_for_restaurant.save()
            return Response({"message": "User rating was successfully added"}, status=status.HTTP_200_OK)

        
# ------------------------------- Restaurant views -----------------------------------
class ResturantViewList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.RestaurantSerializer

    def get(self, request):
        restaurants = models.Restaurant.objects.all().order_by("-pk")
        print(restaurants)
        paginator = CustomPageNumberPagination()

        paginated_restaurants = paginator.paginate_queryset(restaurants, self.request)

         

        serializer = self.serializer_class(paginated_restaurants, many=True)


        return Response({
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        })

    def post(self, request):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RestaurantViewDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.RestaurantSerializer

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]

        # Get all the dishes under this category
        try:
            restaurant = models.Restaurant.objects.get(pk=pk)
            # Get all the dishes under this category
            dishes = models.Dish.objects.filter(restaurant__id=pk).order_by("-pk")

            # Serialize the paginated dishes
            dishes_serializer = serializers.DishSerializer(dishes, many=True)
            serializer = self.serializer_class(restaurant)
            restaurant_details = {
                "id": serializer.data.get("id"),
                "name": serializer.data.get("name"),
                "image": serializer.data.get("image"),
                "description": serializer.data.get("description"),
                "name": serializer.data.get("name"),
                "ratings": serializer.data.get("ratings"),
                "address": serializer.data.get("address"),
                "_dishes": dishes_serializer.data,
            }
            return Response(restaurant_details, status=status.HTTP_200_OK)
        except models.Restaurant.DoesNotExist:
            return Response({"details": "restaurant with id not found"}, status=status.HTTP_404_NOT_FOUND)
        

    def put(self, request, pk):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request,*args, **kwargs):
        pk = kwargs["pk"]
        try:
            restaurant = models.Restaurant.objects.get(pk=pk)
            restaurant.delete()
            return Response({"details": "restaurant has been deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except models.Dish.DoesNotExist:
            return Response({"details": "restaurant with id not found"}, status=status.HTTP_404_NOT_FOUND)
        


# ------------------------------- Driver views -----------------------------------
class DriversViewList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.DriverSerializer

    def get(self, request):

        user = request.user

        if user.role == "chef":
            restaurant = models.Restaurant.objects.get(user=request.user)

            drivers = restaurant.driver_set.all().order_by("-pk")
            paginator = CustomPageNumberPagination()

            paginated_drivers = paginator.paginate_queryset(drivers, self.request)

            serializer = self.serializer_class(paginated_drivers, many=True)


            return Response({
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data,
            })
        
        else:

            drivers = models.Driver.objects.all().order_by("-pk")
            paginator = CustomPageNumberPagination()

            paginated_drivers = paginator.paginate_queryset(drivers, self.request)

            serializer = self.serializer_class(paginated_drivers, many=True)
            
            return Response({
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data,
            })

    
class DriverViewDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]
    serializer_class = serializers.DriverSerializer

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            driver = models.Driver.objects.get(pk=pk)
            serializer = self.serializer_class(driver)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Driver.DoesNotExist:
            return Response({"details": "driver with id not found"}, status=status.HTTP_404_NOT_FOUND)



class DriverDetailRating(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            driver = models.Driver.objects.get(pk=pk)
        except models.Driver.DoesNotExist:
            return Response({
                "message": "driver with id not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the cusumer rating is permitted to 
        # be displayed in the app or approved by the admin

        ratings = models.DriverRating.objects.filter(driver=driver, approved=True)

        serializer = serializers.DriverRatingSerializer(ratings, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        # Get the dish id we are rating
        pk = kwargs["pk"]
        try:
            driver = models.Driver.objects.get(pk=pk)
        except models.Driver.DoesNotExist:
            return Response({"details": "Driver with id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # We get the two accepted data in our payload which are:
        # - rating_number (rating_number must be from 1 - 5)
        # - user (user will be derived from the request user object)

        user = self.request.user
        rating_number = self.request.data.get("rating_number")
        rating_text = self.request.data.get("rating_text")

        if not isinstance(rating_number, int):
            return Response({"message": "rating_number must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        if int(rating_number) > 5 or int(rating_number) < 0:
            return Response({"message": "rating_number must be between 1 - 5"}, status=status.HTTP_400_BAD_REQUEST)

        if not rating_number:
            return Response({"message": "rating_number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_ratings_for_driver = models.DriverRating.objects.get(user=user, driver=driver)
            rating = user_ratings_for_driver
            rating.number = rating_number
            if rating_text:
                rating.text = rating_text
            rating.save()
            return Response({"message": "User rating was successfully updated"}, status=status.HTTP_200_OK)
        except models.DriverRating.DoesNotExist:
            user_ratings_for_driver = models.DriverRating.objects.create(user=user, driver=driver, number=rating_number)
            if rating_text:
                user_ratings_for_driver.text = rating_text
                user_ratings_for_driver.save()
            return Response({"message": "User rating was successfully added"}, status=status.HTTP_200_OK)



# ------------------------------- Order views -----------------------------------

class OrderViewList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, request):
        # Get the user
        # Get all the recent order of the user
        return Response({"message": "Hello"})

    def post(self, request):
        return Response({"message": "Hello"})
    


class OrderViewDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, request, pk):
        return Response({"message": "Hello"})

    def put(self, request, pk):
        return Response({"message": "Hello"})
    
    def delete(self, request, pk):
        return Response({"message": "Hello"})




