from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from rest_framework import generics
from .models import Cart, Category, Order, OrderItem, MenuItem
from .serializers import CartSerializer, CategorySerializer, OrderItemSerializer, MenuItemSerializer, OrderSerializer
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from .permissions import HasGroupPermission
import math
from datetime import date
from .serializers import OrderPutSerializer, CartGetSerializer, OrderIdPutSerializer, OrderIdPatchSerializer
from .serializers import ManagerSerializer
# Create your views here.

class MenuItemView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, HasGroupPermission]
    ordering_fields=['price']
    search_fields = ['title','category__title']
    required_groups = {
        #  'GET': ['__all__'],
        'GET': ['delivery_crew', 'manager', 'customers'],
        'POST': ['manager'],
        # 'PUT': ['manager'],
        # 'PATCH': ['manager'],
        # 'DELETE': ['manager'],
    }
    
    # def get_permissions(self):
    #     if(self.request.method=='GET'):
    #         return [IsAuthenticated(), HasGroupPermission()]

    #     return [IsAuthenticated()]
    
    # def post(self, request, *args, **kwargs):
    #     return Response('403 - Unauthorized', status= status.HTTP_403_FORBIDDEN)
    
    # def put(self, request, *args, **kwargs):
    #     return Response('403 - Unauthorized', status= status.HTTP_403_FORBIDDEN)
    
    # def patch(self, request, *args, **kwargs):
    #     return Response('403 - Unauthorized', status= status.HTTP_403_FORBIDDEN)
    
    # def delete(self, request, *args, **kwargs):
    #     return Response('403 - Unauthorized', status= status.HTTP_403_FORBIDDEN)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        'GET': ['delivery_crew', 'manager', 'customers'],
        'POST': ['manager'],
        'PUT': ['manager'],
        'PATCH': ['manager'],
        'DELETE': ['manager'],
    }

class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = CartSerializer
    required_groups = {
        'GET': ['customers'],
        'POST': ['customers'],
        'DELETE': ['customers'],
    }
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartGetSerializer
        else:
            return CartSerializer
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user = self.request.user).delete()
        return Response('Delete all in Cart', status= status.HTTP_200_OK)
    
    # queryset = Cart.objects.all()
    
    def get_queryset(self):
        queryset = Cart.objects.filter(user = self.request.user).all()
        return queryset


class OrderView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = OrderSerializer
    required_groups = {
        'GET': ['customers', 'manager', 'delivery_crew'],
        'POST': ['customers'],
        # 'DELETE': ['customers'],
    }
    
    ordering_fields=['status', 'date']
    search_fields = ['status', 'date']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        if self.request.method == "POST":
            return OrderPutSerializer
    
    def get_queryset(self):
        if self.request.user.groups.filter(name = 'customers').exists():
            queryset = Order.objects.filter(user = self.request.user).all()
        elif self.request.user.groups.filter(name= 'manager').exists():
        # else:
            queryset = Order.objects.all()
        elif self.request.user.groups.filter(name= 'delivery_crew').exists():
            queryset = Order.objects.filter(delivery_crew = self.request.user).all()
        else:
            queryset = []
        return queryset
    
    def post(self, request, *args, **kwargs):
        cartOrder = Cart.objects.filter(user = self.request.user)
        listCartOders = cartOrder.values_list()
        if len(listCartOders) == 0:
            return Response(f'No item in your Cart, Please buy somethings!', status= status.HTTP_400_BAD_REQUEST)
        total = math.fsum([float(listCartOder[-1]) for listCartOder in listCartOders])
        # total = 100
        delivery_crew = request.POST['delivery_crew']
        order = Order.objects.create(
            user=request.user, 
            status=False, 
            total=total, 
            date=date.today(), 
            delivery_crew=User.objects.get(pk = delivery_crew)
            )
        # return Response(f'Create order successed!', status= status.HTTP_201_CREATED)
        for cartOrderItem in cartOrder.values():
            menuitem = get_object_or_404(MenuItem, id = cartOrderItem['menuitem_id'])
            orderitem = OrderItem.objects.create(
                order=request.user, 
                menuitem=menuitem, 
                quantity=cartOrderItem['quantity'],
                unit_price = cartOrderItem['unit_price'],
                price = cartOrderItem['price'],
                )
            orderitem.save()
        cartOrder.delete()
        return Response(f'Create order(ID: {order.id}) successed!', status= status.HTTP_201_CREATED)
    #     return Response('403 - Unauthorized', status= status.HTTP_403_FORBIDDEN)

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = OrderSerializer
    required_groups = {
        'GET': ['customers'],
        'PUT': ['customers'],
        'PATCH': ['manager', 'delivery_crew'],
        'DELETE': ['manager']
        # 'DELETE': ['customers'],
    }
    
    def get_queryset(self):
        if self.request.user.groups.filter(name = 'customers').exists():
            queryset = Order.objects.filter(user = self.request.user).all()
        elif self.request.user.groups.filter(name= 'manager').exists():
        # else:
            queryset = Order.objects.all()
        elif self.request.user.groups.filter(name= 'delivery_crew').exists():
            queryset = Order.objects.filter(delivery_crew = self.request.user).all()
        else:
            queryset = []
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        if self.request.method == "PATCH":
            return OrderIdPatchSerializer
    
    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk = self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response(f'Status order(#ID: {order.id}) changed to {order.status}!', status= status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk = self.kwargs['pk'])
        order.delete()
        return Response(f'Order(#ID: {order.id}) was deleted!', status= status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        order = Order.objects.filter(user = self.request.user).get(pk = self.kwargs['pk'])
        if not order.status:
            delivery_crew  = get_object_or_404(User, id = request.POST['delivery_crew'])
            order.delivery_crew = delivery_crew
            order.save()
            return Response(f'Order(#ID: {order.id}) was assigned to {delivery_crew.username}!', status= status.HTTP_200_OK)
        else:
            return Response(f'Order(#ID: {order.id}) was assigned to {order.delivery_crew.username} and  the order has been delivered. You not assign to another delivery!', status= status.HTTP_200_OK)
    
class ManagersView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = OrderSerializer
    required_groups = {
        'GET': ['manager'],
        'POST': ['manager'],
        # 'DELETE': ['manager']
        # 'DELETE': ['customers'],
    }
    queryset = User.objects.filter(groups__name='manager')
    serializer_class = ManagerSerializer
    
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='manager')
            managers.user_set.add(user)
            return Response(status=201, data={'message':'User added to Managers group'})

class SingleManagersView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = OrderSerializer
    required_groups = {
        # 'GET': ['manager'],
        # 'POST': ['manager'],
        'DELETE': ['manager']
        # 'DELETE': ['customers'],
    }
    queryset = User.objects.filter(groups__name='manager')
    serializer_class = ManagerSerializer
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='manager')
        managers.user_set.remove(user)
        return Response(status=200, data={'message':'User removed Managers group'})


class DeliveryView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = OrderSerializer
    required_groups = {
        'GET': ['manager'],
        'POST': ['manager'],
        # 'DELETE': ['manager']
        # 'DELETE': ['customers'],
    }
    queryset = User.objects.filter(groups__name='delivery_crew')
    serializer_class = ManagerSerializer
    
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='delivery_crew')
            managers.user_set.add(user)
            return Response(status=201, data={'message':'User added to Delivery-Crew group'})

class SingleDeliveryView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # serializer_class = OrderSerializer
    required_groups = {
        # 'GET': ['manager'],
        # 'POST': ['manager'],
        'DELETE': ['manager']
        # 'DELETE': ['customers'],
    }
    queryset = User.objects.filter(groups__name='delivery_crew')
    serializer_class = ManagerSerializer
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='delivery_crew')
        managers.user_set.remove(user)
        return Response(status=200, data={'message':'User removed Delivery-Crew group'})

# def http_method_list(methods):
#     def http_methods_decorator(func):
#         def function_wrapper(self, request, **kwargs):
#             methods = [method.upper() for method in methods]
#             if not request.method.upper() in methods:
#                 return Response(status=405) # not allowed

#             return func(self, request, **kwargs)
#         return function_wrapper
#     return http_methods_decorator

# @http_method_list(['GET'])
def url_redirect_me(request):
    return HttpResponseRedirect("/api/auth/users/me")