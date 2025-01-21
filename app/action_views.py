from functools import reduce
import stripe

from decouple import config
# views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, Dish, Restaurant, Driver, Payment
from .serializers import OrderSerializer, OrderItemSerializer, DishSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from app.permissions import IsUserVerified
from rest_framework.views import APIView


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    # authentication_classes = []
    # permission_classes = []
    # pagination_class = []

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    # authentication_classes = []
    # permission_classes = []
    # pagination_class = []

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created_at')
    


    # def retrieve(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())  # Get all instances
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data) 

    def create(self, request, *args, **kwargs):
        
        data = request.data
        items_data = data.pop('items')
        if len(items_data) < 1:
            return Response({"message": "There must be ordered items in the payload"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(items_data, list):
            return Response({"message": "Invalid data structure for items. Items must be an array of ordered items."}, status=status.HTTP_400_BAD_REQUEST)
        
        total_price = reduce(lambda x, y: x + (float(y.get("amount", 0)) * int(y.get("quantity", 0))), items_data, 0)

        # print("Total price", total_price == data.get("total_price"))

        if float(total_price) != float(data.get("total_price")):
            return Response({"message": "Conflict in total price. There is a difference between the total price of items and that of the general total price."})
        # Assuming the request data has 'user', 'items', and other necessary fields
        # serializer = self.get_serializer(data=data)
        # items = data.get("items")
        data.pop("user")
        order = Order.objects.create(user=request.user, **data)
        for item in items_data:
            dish_id = item.get("dish_id")
            restaurant_id = item.get("restaurant_id")
            amount = item.get("amount")
            quantity = item.get("quantity")
            try:
                dish = Dish.objects.get(id=item.pop('dish_id'))
            except Dish.DoesNotExist:
                return Response({"message": f"Dish with id: {dish_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            try:
                restaurant = Restaurant.objects.get(id=item.pop("restaurant_id"))
            except Restaurant.DoesNotExist:
                return Response({"message": f"Restaurant with id: {restaurant_id} does not exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            OrderItem.objects.create(order=order, dish=dish, restaurant=restaurant, **item)
            
            print("Dish Restaurant: ", dish.restaurant)
            print("Real Restaurant: ", restaurant)
            # Here, we retrieve and update the restaurant balance
            try:
                restaurant_to_update_balance = Restaurant.objects.get(id=restaurant_id)
                balance_to_update_for_restaurant = int(amount) * int(quantity)
                restaurant_to_update_balance.balance = balance_to_update_for_restaurant
                restaurant_to_update_balance.save()
                print("The total balance part worked! ")
            except Restaurant.DoesNotExist:
                return Response({"message":f"Restaurant with id: {restaurant_id} does not exists"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message":f"Something else happened here: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class OrderCustomerListView(APIView):
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        payment_status = data.get("payment_status", False)
        
        if not data.get("items"):
            return Response({"message": "No items or colletion of items in the payload -- items field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        items_data = data.pop('items')
        if len(items_data) < 1:
            return Response({"message": "There must be ordered items in the payload"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(items_data, list):
            return Response({"message": "Invalid data structure for items. Items must be an array of ordered items."}, status=status.HTTP_400_BAD_REQUEST)
        
        total_price = reduce(lambda x, y: x + (float(y.get("amount", 0)) * int(y.get("quantity", 0))), items_data, 0)

        # print("Total price", total_price == data.get("total_price"))

        if int(total_price) != int(data.get("total_price")):
            return Response({"message": "Conflict in total price. There is a difference between the total price of items and that of the general total price."})
        # Assuming the request data has 'user', 'items', and other necessary fields
        # serializer = self.get_serializer(data=data)
        # items = data.get("items")
        # if data.get("user"):
        #     data.pop("user")
        order = Order.objects.create(user=request.user, **data)
        for item in items_data:
            dish_id = item.get("dish_id")
            restaurant_id = item.get("restaurant_id")
            amount = item.get("amount")
            quantity = item.get("quantity")


            try:
                dish = Dish.objects.get(id=item.pop('dish_id'))
            except Dish.DoesNotExist:
                return Response({"message": f"Dish with id: {dish_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            try:
                restaurant = Restaurant.objects.get(id=item.pop("restaurant_id"))
            except Restaurant.DoesNotExist:
                return Response({"message": f"Restaurant with id: {restaurant_id} does not exists"}, status=status.HTTP_404_NOT_FOUND)
            
            if int(amount) != int(dish.price):
                return Response({"message": f"The amount {int(amount)} entered for dish with id {dish.id} does not correlate with the price of dish {dish.price}"}, status=status.HTTP_400_BAD_REQUEST)
            
            OrderItem.objects.create(
                order=order, 
                dish=dish, 
                restaurant=restaurant, 
                customer=request.user, 
                **item
            )

            # Check if the dish belongs to the restaurant
            if dish.restaurant != restaurant:
                return Response({"message": f"The dish id: {dish_id} and the resturant_id: {restaurant_id} does not correllate. In other words, it is not the restaurant that has the selected dish."})
            
            # Here, we retrieve and update the restaurant balance
            try:
                restaurant_to_update_balance = Restaurant.objects.get(id=restaurant_id)
                balance_to_update_for_restaurant = int(amount) * int(quantity)
                restaurant_to_update_balance.balance += balance_to_update_for_restaurant
                restaurant_to_update_balance.save()
                print("The total balance part worked! ")
            except Restaurant.DoesNotExist:
                return Response({"message":f"Restaurant with id: {restaurant_id} does not exists"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message":f"Something else happened here: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Payment instance
        Payment.objects.create(
            user=request.user,
            order=order, 
            payment_method="flutterwave", 
            transaction_id="autogenerated_id", 
            amount=total_price,
            status=payment_status,
        )
        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    



class OrderItemsListForAllUsers(APIView):
    serializer_class = OrderItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Check the user that is requesting for the ordered items
        # If the user is a customer, fetch all Customer his order
        # If the user is a restaurant, get all the orders for that restaurant
        # If the user is a driver, get all the orders for the assigned driver

        query_params = request.query_params

        # Check the query parameters to the option key
        # If the option is history, let all the orderitems completed and cancelled be shown
        # If the option is ongoing, let all the orderitems pending be shown
        # Else if option is not specified, let all the orderitems be shown
        option = query_params.get("option")
        ordereditems = OrderItem.objects.all()
        if option == "history":
            ordereditems = ordereditems.exclude(status="pending")
        elif option == "ongoing":
            ordereditems = ordereditems.filter(status="pending").exclude(status="completed").exclude(status="cancelled")
        else:
            pass

        user = request.user

        user_is_customer = user.role == "customer"
        user_is_driver = user.role == "logistics"
        user_is_restaurant = user.role == "chef"

        # print("user_is_customer: ", user_is_customer)
        # print("user_is_driver: ", user_is_driver)
        # print("user_is_restaurant: ", user_is_restaurant)

        if user_is_customer:
            # User is a customer
            ordereditems = ordereditems.filter(order__user_id=request.user.id)
            serializer = self.serializer_class(ordereditems, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user_is_restaurant:
            ordereditems = ordereditems.filter(restaurant__user_id=user.id)
            # User is a Restaurant or Kitchen
            serializer = self.serializer_class(ordereditems, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user_is_driver:
            # User is a driver
            ordereditems = ordereditems.filter(driver__user_id=user.id)
            serializer = self.serializer_class(ordereditems, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User must be one of the following: restaurant, driver or customer"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class OrderItemsDetailsForAllUsers(APIView):
    serializer_class = OrderItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            orderitem = OrderItem.objects.get(pk=pk)
        except OrderItem.DoesNotExist:
            return Response({"message": f"Order item with id: {pk} does not exist"})
        
        user = request.user

        user_is_customer = user.role == "customer"
        user_is_driver = user.role == "logistics"
        user_is_restaurant = user.role == "chef"

        serializer = self.serializer_class(orderitem)

        # Check the user permission if the user is either of the following:
        # customer, chef and driver

        if user_is_customer:
            # Check if user is customer and it is them who made the order
            if orderitem.order.user.id != user.id:
                return Response({"message": "User does not have permission to view this order item"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif user_is_restaurant:
            # Check if user is restaurant and it is them who are receiving the order
            if orderitem.restaurant.user.id != user.id:
                return Response({"message": "User does not have permission to view this order item"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif user_is_driver:
            # Check if user is driver and it is them who are delivering or being assigned to the order
            if not orderitem.driver:
                return Response({"message": "User does not have permission to view this order item"}, status=status.HTTP_401_UNAUTHORIZED)
            if orderitem.driver.user.id != user.id:
                return Response({"message": "User does not have permission to view this order item"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User must be one of the following: restaurant, driver or customer"}, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, *args, **kwargs):
        # Get the driver or status --- completed, pending, cancelled

        pk = kwargs["pk"]
        
        data = request.data
        # The current user can send the driver_id or the status, at anytime they wishes
        

        # Get the orderitem
        try:
            orderitem = OrderItem.objects.get(pk=pk)
        except OrderItem.DoesNotExist:
            return Response({"message": "Ordered item does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get OrderItemSerializer
        serializer = self.serializer_class(orderitem, data=request.data)
        # If there is no error, save it
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order item updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_201_CREATED)
    
    

# Assign Driver to orderitem
# ---- Alternative view
@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def assign_driver_to_orderitem(request):
    user = request.user

    # Driver id
    data = request.data
    driver_id = request.data.get("driver_id")
    orderitem_id = request.data.get("orderitem_id")

    # Action to assign (add) or unassign (remove)
    query_params = request.query_params
    option = query_params.get("option")

    if not driver_id:
        return Response({"message": "driver_id field is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not option:
        return Response({"message": "option query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    if user.role != "chef":
        return Response({"message": "User must  be a restaurant"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reataurant = Restaurant.objects.get(user=user)
        orderitem = OrderItem.objects.get(pk=orderitem_id)
        restaurant_driver = reataurant.driver_set.get(id=driver_id)
    except Restaurant.DoesNotExist:
        return Response({"message": "User must be a restaurant"}, status=status.HTTP_404_NOT_FOUND)
    except OrderItem.DoesNotExist:
        return Response({"message": "Order item does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except Driver.DoesNotExist:
        return Response({"message": f"Driver with id: {driver_id} does not exist your restaurant"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check user input -- option
    if option == "add_driver":
        orderitem.driver = restaurant_driver
        orderitem.save()
        return Response({"message": f"Driver: {restaurant_driver.user.email} assigned successfully to ordered item"}, status=status.HTTP_200_OK)
    elif option == "remove_driver":
        orderitem.driver = None
        orderitem.save()
        return Response({"message": f"Driver was removed successfully from the ordered item"}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Select a valid option --- add_driver or remove_driver"}, status=status.HTTP_400_BAD_REQUEST)






@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsUserVerified])
def payment_intent_stripe(request):
    stripe.api_key = config("STRIPE_SECRET_KEY")
    amount = request.data.get("amount")
    currency_code = request.data.get("currency_code")

    if not amount:
        return Response({"message": f"amount field is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not currency_code:
        return Response({"message": f"currency_code field is required"}, status=status.HTTP_400_BAD_REQUEST)

    amount = int(float(request.data.get("amount")))
    

    try:
        payment_intent_stripe = stripe.PaymentIntent.create(
            amount=int(float(amount)),
            currency=currency_code,
            automatic_payment_methods={"enabled": True},
        )
        return Response({"payment_intent_secret": payment_intent_stripe.client_secret}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"Something went wrong: {e}"}, status=status.HTTP_400_BAD_REQUEST)

