from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem, Category
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User
import bleach

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category']
        
    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        # attrs['price'] = bleach.clean(attrs['price'])
        # attrs['featured'] = bleach.clean(attrs['featured'])
        # attrs['category'] = bleach.clean(attrs['category'])
        return super().validate(attrs)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']
    
    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        # attrs['slug'] = bleach.clean(attrs['slug'])
        return super().validate(attrs)

class CartGetSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
        )
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 
                  'unit_price', 
                  'price',
                  ]
        depth = 1
        
        
class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
        )

    menuitem = serializers.PrimaryKeyRelatedField(
            queryset=MenuItem.objects.all(),
        )
    
    # menuitem = MenuItemSerializer()
    
    # menuitem = serializers.HyperlinkedRelatedField(
    #     queryset = MenuItem.objects.all(),
    #     view_name='menuitems-detail'
    #     )
    
    # extra_kwargs = {
    #     'quantity': {
    #         # 'max_value': 5,
    #         'min_value': 1,
    #     }
    # }


    # def get_unit_price(self, product:Cart):
    #     return product.menuitem.price
    
    # def get_price(self, product:Cart):
    #     return product.menuitem.price * product.quantity
    
    # unit_price = serializers.SerializerMethodField()
    # price = serializers.SerializerMethodField()
    
    # unit_price = serializers.SerializerMethodField(method_name = 'calculate_unit_price')
    # price = serializers.SerializerMethodField(method_name = 'calculate_price')
    # def calculate_unit_price(self, product:Cart):
    #     return product.menuitem.price
    
    # def calculate_price(self, product:Cart):
    #     return product.menuitem.price * product.quantity

    # def validate(self, attrs):
        # attrs['user'] = bleach.clean(attrs['user'])
        # attrs['menuitem'] = bleach.clean(attrs['menuitem'])
        # attrs['quantity'] = bleach.clean(attrs['quantity'])
        # attrs['unit_price'] = bleach.clean(attrs['unit_price'])
        # attrs['price'] = bleach.clean(attrs['price'])
        # return super().validate(attrs)

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 
                  'unit_price', 
                  'price',
                  ]
        depth = 1
        # read_only_fields = ['menuitem']
    
    
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
        )
    
    delivery_crew = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.filter(groups__name='delivery_crew'),
        )
    
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']
        
    # def validate(self, attrs):
        # attrs['user'] = bleach.clean(attrs['user'])
        # attrs['status'] = bleach.clean(attrs['status'])
        # attrs['total'] = bleach.clean(attrs['total'])
        # attrs['date'] = bleach.clean(attrs['date'])
        # return super().validate(attrs)
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
    
    # def validate(self, attrs):
        # attrs['order'] = bleach.clean(attrs['order'])
        # attrs['menuitem'] = bleach.clean(attrs['menuitem'])
        # attrs['quantity'] = bleach.clean(attrs['quantity'])
        # attrs['unit_price'] = bleach.clean(attrs['unit_price'])
        # attrs['price'] = bleach.clean(attrs['price'])
        # return super().validate(attrs)

class OrderPutSerializer(serializers.ModelSerializer):
    delivery_crew = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.filter(groups__name='delivery_crew'),
        )
    class Meta():
        model = Order
        fields = ['delivery_crew']
        
class OrderIdPatchSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['status']

class OrderIdPutSerializer(serializers.ModelSerializer):
    delivery_crew = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.filter(groups__name='delivery_crew'),
        )
    class Meta():
        model = Order
        fields = ['delivery_crew']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']