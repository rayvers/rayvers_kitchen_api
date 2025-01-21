from django import test
from app.models import (
    Category, Restaurant,
    RestaurantRating,

)
from django.contrib.auth import get_user_model

# Get the User model to be used throughout the app
User = get_user_model()


class TestCategory(test.TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(
            name="snacks",
            image_url="https://reyverskitchen.com/image_snacks.png"
        )
        return super().setUp()

    def test_if_category_exists(self):
        category = Category.objects.get(id=1)
        self.assertTrue(category)
        self.assertEqual(category.name, "snacks")
        self.assertEqual(category.image_url, "https://reyverskitchen.com/image_snacks.png")

    def test_category_str_(self):
        self.assertEqual(self.category.__str__(), "snacks")


class TestRestaurant(test.TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="john@don.com",
            password="my_ecrypted_password"
        )
        self.restaurant = Restaurant.objects.create(
            user=self.user,
            kitchen_id="THIFGSJH",
            image_url="https://reyverskitchen.com/image_snacks.png",
            name="James Restaurant",
            description="James Restaurant is the best",
            address="5th Wallstreet",
            balance="0.00"
        )
        return super().setUp()
    
    def test_if_restaurant_was_created(self):
        self.assertTrue(self.restaurant)
        self.assertEqual(self.restaurant.user, self.user)
        self.assertEqual(self.restaurant.kitchen_id, "THIFGSJH")
        self.assertEqual(self.restaurant.image_url, "https://reyverskitchen.com/image_snacks.png")
        self.assertEqual(self.restaurant.description, "James Restaurant is the best")
        self.assertEqual(self.restaurant.address, "5th Wallstreet")
        self.assertEqual(self.restaurant.balance, "0.00")

    def test_if_restaurant_properties_give_expected_results(self):
        self.assertEqual(
            self.restaurant.__str__(), 
            f"Restaurant: {self.restaurant.user.email}"
        )
        self.assertEqual(self.restaurant._dishes, [])
        self.assertEqual(self.restaurant.ratings, 0)
        self.assertEqual(self.restaurant._meta.verbose_name_plural, "Restaurants")
        self.assertEqual(self.restaurant._meta.verbose_name, "Restaurant")
    

class TestRestaurantRating(test.TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="john@don.com",
            password="my_ecrypted_password"
        )
        self.restaurant = Restaurant.objects.create(
            user=self.user,
            kitchen_id="THIFGSJH",
            image_url="https://reyverskitchen.com/image_snacks.png",
            name="James Restaurant",
            description="James Restaurant is the best",
            address="5th Wallstreet",
            balance="0.00"
        )
        self.restaurant_rating = RestaurantRating.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            text="This is the best restaurant",
            number=3
        )
        return super().setUp()
    
    def test_if_restaurant_ratings_exists(self):
        restaurant_rating = RestaurantRating.objects.get(id=1)
        self.assertEqual(self.restaurant_rating, restaurant_rating)
        self.assertEqual(self.restaurant_rating.user, self.user)
        self.assertEqual(self.restaurant_rating.restaurant, self.restaurant)
        self.assertEqual(self.restaurant_rating.text, "This is the best restaurant")
        self.assertEqual(self.restaurant_rating.number, 3)

    def test_if_restaurant_ratings_properties_give_expected_results(self):
        self.assertEqual(
            self.restaurant_rating.__str__(), 
            str(self.user.email) + ' -- ' + str(self.restaurant_rating.number) + " -- " + str(self.restaurant.name)
        )
        self.assertEqual(self.restaurant_rating._meta.verbose_name_plural, "Restaurant Ratings")
        self.assertEqual(self.restaurant_rating._meta.verbose_name, "Restaurant Rating")


class TestImageURL(test.TestCase):
    def setUp(self) -> None:
        return super().setUp()


    
    






    




