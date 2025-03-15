# models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from authentication.models import UserProfile

import random
import string



User = get_user_model()

def generate_random_username(length, max_attempts=100):
    for _ in range(max_attempts):
        random_username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
        if not User.objects.filter(username=random_username).exists():
            return random_username
    raise ValueError('Could not generate a unique username after {} attempts'.format(max_attempts))

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    image_url = models.CharField(max_length=2000, unique=True, blank=True, null=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Category"

class Restaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kitchen_id = models.CharField(_("Kitchen id"), max_length=20, blank=True, null=False)
    image_url = models.CharField(max_length=2000, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField(blank=True)
    balance = models.DecimalField(default=0.0, max_digits=100, decimal_places=2)
    
    # Other fields as needed will be here...

    @property
    def ratings(self):
        all_ratings = self.restaurant_rated.all()
        min_ratings_required = 1  # Minimum number of ratings required
        
        if len(all_ratings) >= min_ratings_required:
            total_ratings = sum(rating.number for rating in all_ratings)
            average_rating = total_ratings / len(all_ratings)
            return round(average_rating, 1)
        return 0

    def __str__(self):
        return f"Restaurant: {self.user.email}"
    

    @property
    def _dishes(self):
        dishes = self.dishes.all().order_by("-pk")
        all_dishes = [{
            "id": dish.id, 
            "name": dish.name, 
            "ratings": dish.ratings,
            "description": dish.description,
            "delivery_options": dish.delivery_options,
            "time_duration": dish.time_duration,
            "get_category": dish.get_category,
            "price": dish.price,
            "_ingredients": dish._ingredients,
            "get_category": dish.get_category,
            "favourite": [fav.id for fav in dish.favourite.all()],
            "get_images": dish.get_all_image_urls_added_from_frontend,
        } for dish in dishes]
        return all_dishes
    
    class Meta:
        verbose_name_plural = "Restaurants"
        verbose_name = "Restaurant"
    
class RestaurantRating(models.Model):
    number = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurant_ratings")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_rated")
    text = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    @property
    def user_data(self):
        user = self.user
        profile = UserProfile.objects.get(user=user)
        user_details = {
            "display_image": profile.image_url,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
        return user_details

    def __str__(self) -> str:
        return str(self.user.email) + ' -- ' + str(self.number) + " -- " + str(self.restaurant.name)
    class Meta:
        verbose_name_plural = "Restaurant Ratings"
        verbose_name = "Restaurant Rating"


# Listens for chef that was created
@receiver(post_save, sender=User)
def create_restaurant(sender, instance=None, created=False, **kwargs):
    if created and instance.role == "chef":
        # Create a restaurant here
        restaurant = Restaurant.objects.create(user=instance)
        
        # Generate a unique username for the restaurant
        username = generate_random_username(8)
        while Restaurant.objects.filter(kitchen_id=username).exists():
            username = generate_random_username(8)
        # Set the username for the user and the restaurant
        instance.username = username
        instance.save()
        restaurant.kitchen_id = username
        restaurant.save()
        # print("A restaurant was created")

    

class ImageURL(models.Model):
    url = models.CharField(max_length=1000, blank=True, null=True)
    

    def __str__(self):
        return self.url
    
    class Meta:
        verbose_name_plural = "Images URLs"
        verbose_name = "Image URL"

class Ingredient(models.Model):
    image_url = models.CharField(max_length=2000, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)
    

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = "Ingredients"
        verbose_name = "Ingredient"

class Dish(models.Model):
    DELIVERY_OPTIONS = [
        ("free", "free"),
        ("paid", "paid")
    ]
    image_urls = models.ManyToManyField(ImageURL, related_name="image_urls", blank=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=False, null=False)
    delivery_options = models.CharField(choices=DELIVERY_OPTIONS, max_length=5, default="paid")
    time_duration = models.IntegerField(verbose_name="Time it takes to deliver.", help_text="In minutes.", default=0, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dish_category") 
    price = models.IntegerField()
    ingredients = models.ManyToManyField(Ingredient, related_name="dish_ingredients")
    restaurant = models.ForeignKey(Restaurant, related_name="dishes", on_delete=models.CASCADE)

    favourite = models.ManyToManyField(User, related_name="favourites", blank=True)

    @property
    def ratings(self):
        all_ratings = self.dishes_rated.all()
        min_ratings_required = 1  # Minimum number of ratings required
        
        if len(all_ratings) >= min_ratings_required:
            total_ratings = sum(rating.number for rating in all_ratings)
            average_rating = total_ratings / len(all_ratings)
            return round(average_rating, 1)
        return 0

    @property
    def _ingredients(self):
        all_ingredients = [ing.name for ing in self.ingredients.all()]
        return all_ingredients

    @property
    def restaurant_details(self):
        restaurant = self.restaurant
        return {
            "name": restaurant.name,
            "ratings": restaurant.ratings,
        }

    @property
    def get_images(self):
        images = self.images.all()
        new_list = list(map(lambda x: {"label": x.label, "url":x.file.url}, images))
        return new_list
    
    @property
    def get_all_image_urls_added_from_frontend(self):
        images = self.image_urls.all()
        new_list = list(map(lambda x: {"url": x.url}, images))
        return new_list
    
    @property
    def get_category(self):
        return {
            "id": self.id,
            "name": self.category.name,
            "image": self.category.image_url
        }

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Dishes"
        verbose_name = "Dish"


class RestaurantWithdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurant_user_withdrawal", blank=True)
    account_bank = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=200, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    narration = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return self.user.email
    
    @property
    def restaurant(self):
        _restaurant = Restaurant.objects.get(user=self.user)

        return {
            "id": _restaurant.id,
            "name": _restaurant.name,
            "description": _restaurant.description,
            "ratings": _restaurant.ratings,
            "image_url": _restaurant.image_url,
            "address": _restaurant.address,
            "balance": _restaurant.balance,
        }
    
    @property
    def get_payment_info(self):
        details = {
            "user_email": self.user.email,
            "account_bank": self.account_bank,
            "amount": self.amount,
            "currency_code": self.currency,
            "narration": self.narration,
            "reference": self.reference
        }
        return details



class DishRating(models.Model):
    number = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dish_ratings")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="dishes_rated")
    text = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    @property
    def user_data(self):
        user = self.user
        profile = UserProfile.objects.get(user=user)
        user_details = {
            "display_image": profile.image_url if profile.image_url else profile.get_image_url,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
        return user_details


    def __str__(self) -> str:
        return str(self.user.email) + ' -- ' + self.dish.name + ' -- ' + str(self.number)
    
    class Meta:
        verbose_name_plural = "Dish Ratings"
        verbose_name = "Dish Rating"


class Order(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_delivered = models.BooleanField(default=False)
    
    payment_status = models.BooleanField(verbose_name="Has Paid?", default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"
    
    class Meta:
        verbose_name_plural = "Orders"
        verbose_name = "Order"

class OrderItem(models.Model):
    ORDER_STATUS_CHOICES = [
        ("completed", "completed"),
        ("pending", "pending"), 
        ("cancelled", "cancelled")
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, null=True, blank=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=10, default="pending")
    quantity = models.PositiveIntegerField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return f"{self.quantity} x {self.dish.name} in Order #{self.order.id}"
    
    class Meta:
        verbose_name_plural = "Order Items"
        verbose_name = "Order Item"

class Driver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    driver_id = models.CharField(_("Driver id"), max_length=20, blank=True, null=False)
    name = models.CharField(_("Driver Name"), max_length=100, blank=True, null=False)

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, blank=True, null=True)
    vehicle_image_url = models.CharField(max_length=2000, blank=True, null=True)
    vehicle_color = models.CharField(max_length=40, blank=True, null=True)
    vehicle_description = models.TextField(blank=True, null=False)
    vehicle_number = models.CharField(max_length=40, blank=True, null=False)
    available = models.BooleanField(default=False)
    current_location_latitude = models.DecimalField(max_digits=10, decimal_places=10, null=True, blank=True)
    current_location_longitude = models.DecimalField(max_digits=10, decimal_places=10, null=True, blank=True)

    @property
    def ratings(self):
        all_ratings = self.driver_rated.all()
        min_ratings_required = 1  # Minimum number of ratings required
        
        if len(all_ratings) >= min_ratings_required:
            total_ratings = sum(rating.number for rating in all_ratings)
            average_rating = total_ratings / len(all_ratings)
            return round(average_rating, 1)
        return 0
    
    @property
    def profile_details(self):
        profile = self.user.profile
        profile_deails = {
            "name": profile.name,
            "image_url": profile.image_url,
            "date_of_birth": profile.date_of_birth,
            "phone_number": profile.phone_number,
            "bio": profile.bio
        }
        return profile_deails
    

    def __str__(self):
        return f"Driver: {self.user.email}"
    
    class Meta:
        verbose_name_plural = "Drivers"
        verbose_name = "Driver"

@receiver(post_save, sender=User)
def create_driver(sender, instance=None, created=False, **kwargs):
    if created and instance.role == "logistics":
        # Create a driver here
        driver = Driver.objects.create(user=instance)
        # Generate a unique username for the driver
        username = generate_random_username(8)
        while Driver.objects.filter(driver_id=username).exists():
            username = generate_random_username(8)
        # Set the username for the user and the driver
        instance.username = username
        instance.save()
        driver.driver_id = username
        driver.save()
        # print("A driver was created")
        

class DeliveryStatus(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status_choices = [
        ('PENDING', 'Pending'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='PENDING')

    def __str__(self):
        return f"Status for Order #{self.order.id}: {self.status}"
    
    class Meta:
        verbose_name_plural = "Delivery Statuses"
        verbose_name = "Delivery Status"


class DriverRating(models.Model):
    number = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="driver_ratings")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="driver_rated")
    text = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    @property
    def user_data(self):
        user = self.user
        profile = UserProfile.objects.get(user=user)
        user_details = {
            "display_image": profile.image_url,
            "name": profile.name,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
        return user_details

    def __str__(self) -> str:
        return str(self.user.email) + ' -- ' + str(self.number) + " -- " + str(self.driver.name)
    class Meta:
        verbose_name_plural = "Driver Ratings"
        verbose_name = "Driver Rating"

class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Dish, through='CartItem')

    def __str__(self):
        return f"Shopping Cart for {self.user.email}"
    
    class Meta:
        verbose_name_plural = "Shopping Carts"
        verbose_name = "Cart"

class CartItem(models.Model):
    food_item = models.ForeignKey(Dish, on_delete=models.CASCADE)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} in {self.cart}"
    
    class Meta:
        verbose_name_plural = "Cart Items"
        verbose_name = "Cart Item"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} via {self.payment_method} by {self.user.email}"

    class Meta:
        verbose_name_plural = "Payments"
        verbose_name = "Payment"

class PersonalMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email}"
    
    class Meta:
        verbose_name_plural = "Personal Messages"
        verbose_name = "Personal Message"





