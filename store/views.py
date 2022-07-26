from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from .serializers import CreateOrderSerializer, CustomerSerializer, OrderSerializer, OwnerCreateSerializer, OwnerSerializer, ProductSerializer, ReviewSerializer, ShopSerializer
from .models import Cart, CartItem, Customer, Order, OrderItem, Owner, Product, Review, Shop

from pprint import pprint


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    # queryset = Product.objects.all()

    def get_queryset(self):
        url_param = self.kwargs
        if ('shop_pk' in url_param):
            return Product.objects.filter(shop_id=url_param['shop_pk'])
        else:
            return Product.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # Wanted to do queryset = Review.objects.filter(product_id = self.kwargs['product_id'])
    # However, self cannot be found
    # Hence, use get_queryset

    def get_queryset(self):
        url_param = self.kwargs
        pprint(self.kwargs)
        pprint('shop_pk' in url_param)
        if ('product_pk' in url_param):
            return Review.objects.filter(product_id=self.kwargs['product_pk'])
        elif ('shop_pk' in url_param):
            return Review.objects.filter(shop_id=self.kwargs['shop_pk'])
        else:
            return None


class OwnerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Owner.objects.all()
    permission_classes = [IsAuthenticated]
    # serializer_class = OwnerSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return OwnerCreateSerializer
        return OwnerSerializer

    def get_permissions(self):
        if self.request.method == 'GET' or self.request.method == "POST":
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (current_owner, created) = Owner.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = OwnerSerializer(current_owner)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = OwnerSerializer(
                current_owner, request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    # We don't really need a list of customers
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    # Available on list view /customers/me

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (current_customer, created) = Customer.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(current_customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(
                current_customer, request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    """
    Only Vendors can see orders
    """

    def get_queryset(self):
        if (self.request.user.is_staff):
            return Order.objects.all()
        if(self.request.user.is_vendor):
            current_owner = Owner.get(user=self.request.user)
            shop = Shop.objects.get(owner=current_owner)
            return shop.orders

    def get_serializer_class(self):
        if (self.request.method == "GET"):
            return OrderSerializer
        if (self.request.method == "POST"):
            return CreateOrderSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ['list']:
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        current_customer = Customer.objects.get(user=request.user)
        newest_cart = Cart.objects.filter(customer=current_customer,
                                          is_checkout=False).first()
        current_cart_items = CartItem.objects.filter(
            cart=newest_cart).values('product', 'quantity')
        order = Order.objects.create(
            shop=newest_cart.shop, customer=current_customer)

        for item in current_cart_items:
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity)

        newest_cart.is_checkout = True
        newest_cart.save()

        return Response(data={}, status=status.HTTP_201_CREATED)


"""
POST /store/orders
    - Cart ID

1) Set current cart of Customer to is_order = True
2) Create a new order by iterating through the cart_items and creating corresponding order_items
3) Create new cart instance and tie it to this customer
"""


"""
Customer
I can add things into my cart
If I logout and come back, my cart will still be there

"""
