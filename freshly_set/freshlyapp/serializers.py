from rest_framework import serializers

from .models import Blog, Product, Garden, Comment, Like, Share, Poll, Vote, IDVerification, Review, Farmer, Cart, CartItem, Banner, Category
from django.contrib.auth import get_user_model, authenticate
from rest_framework.validators import ValidationError
from django.contrib.auth.models import User
from better_profanity import profanity

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel  # This is still the built-in User model
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise ValidationError('Invalid credentials')
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, data):
        if data.get('price', 0) < 0:
            raise serializers.ValidationError(
                {'price': 'Price cannot be negative.'})

        if not (0.01 <= data.get('price', 0) <= 99999.99):
            raise serializers.ValidationError(
                {'price': 'Price must be between 0.01 and 99999.99.'})

        if len(str(data.get('price', 0)).split('.')[-1]) > 2:
            raise serializers.ValidationError(
                {'price': 'Price cannot have more than two decimal places.'})

        if data.get('qtty', 0) < 0:
            raise serializers.ValidationError(
                {'qtty': 'Quantity cannot be negative.'})

        if data.get('qtty', 0) > 10000:
            raise serializers.ValidationError(
                {'qtty': 'Quantity cannot exceed 10,000.'})

        if len(data.get('name', '').strip()) == 0:
            raise serializers.ValidationError(
                {'name': 'Name cannot be empty.'})

        if len(data.get('name', '')) > 255:
            raise serializers.ValidationError(
                {'name': 'Name cannot exceed 255 characters.'})

        if len(data.get('desc', '')) < 10:
            raise serializers.ValidationError(
                {'desc': 'Description is too short. It should be at least 10 characters long.'})

        if profanity.contains_profanity(data.get('desc', '')):
            raise serializers.ValidationError(
                {'desc': 'Description contains prohibited or inappropriate content.'})

        return data


class ReviewSerializer(serializers.ModelSerializer):
    # Nested serializer to display product details
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )  # To allow assignment of product by ID

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_id',
                  'rating', 'comment', 'created_at']


class FarmerSerializer(serializers.ModelSerializer):
    # Nested serializer to display product details
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )  # To allow assignment of product by ID

    class Meta:
        model = Farmer
        fields = ['id', 'product', 'product_id', 'name', 'email', 'phone']


class GardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garden
        fields = ['id', 'name', 'location', 'size', 'description']


class BlogSerializer(serializers.ModelSerializer):
    # comments = serializers.StringRelatedField(many=True)
    # likes = serializers.StringRelatedField(many=True)
    # shares = serializers.StringRelatedField(many=True)

    class Meta:
        model = Blog
        fields = ['id', 'user', 'title', 'content',
                  'image', 'comments', 'likes', 'shares']
        # These fields are typically read-only
        read_only_fields = ['id', 'comments', 'likes', 'shares']

# Created serializers for Blog, Comment, Like, and Share.


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'blog', 'user', 'content', 'created_at', 'updated_at']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'blog', 'user']


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'blog', 'user', 'shared_at']

# Polls serializer


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'choice', 'created_at']


class PollSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    vote_counts = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'created_at',
                  'created_by', 'votes', 'vote_counts']

    def get_vote_counts(self, obj):
        return obj.vote_counts()

# IDverification


class IDVerificationSerializer(serializers.ModelSerializer):
    id_document_number = serializers.CharField(required=True)
    document_image = serializers.ImageField(required=True)
    photo_image = serializers.ImageField(required=True)

    class Meta:
        model = IDVerification
        fields = ['id_document_type', 'id_document_number',
                  'document_image', 'photo_image', 'is_verified']

    def validate(self, data):
        """
        Validate and verify the ID number and photo.
        """
        instance = self.instance if self.instance else IDVerification(**data)

        # Validate ID number format
        if not instance.verify_id_number():
            raise serializers.ValidationError(
                {"id_document_number": "Invalid ID number format for the selected document type."})

        # Validate and verify photo
        if not instance.verify_photo():
            raise serializers.ValidationError(
                {"photo_image": "Photo verification failed. The photo does not match the ID document."})

        return data

    def update(self, instance, validated_data):
        """
        Update the instance after verification and mark it as verified if successful.
        """
        instance.id_document_type = validated_data.get(
            'id_document_type', instance.id_document_type)
        instance.id_document_number = validated_data.get(
            'id_document_number', instance.id_document_number)
        instance.document_image = validated_data.get(
            'document_image', instance.document_image)
        instance.photo_image = validated_data.get(
            'photo_image', instance.photo_image)

        # Perform verification
        if instance.verify_user():
            instance.is_verified = True
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                "Verification failed. ID number or photo is not correct.")


# Banner Serializer for Marketplace Page

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'url',
                  'active', 'created_at', 'category', "countdown"]


# Category Serializer:

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # Specify the fields you want in the API
        fields = ['id', 'name', 'description']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

    def validate(self, data):
        # Quantity validation
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError(
                {'quantity': 'Quantity must be at least 1.'})

        # Max quantity validation
        if data.get('quantity', 0) > CartItem.MAX_QUANTITY:
            raise serializers.ValidationError(
                {'quantity': f'Quantity cannot exceed {CartItem.MAX_QUANTITY} per product.'})

        # Stock availability validation
        if data['quantity'] > data['product'].qtty:
            raise serializers.ValidationError(
                {'quantity': f'Not enough stock. Available stock is {data["product"].qtty}.'})

        # Ensure product exists
        if not data.get('product'):
            raise serializers.ValidationError(
                {'product': 'Product must exist for the cart item.'})

        return data


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

    def validate(self, data):
        # Ensure user or session is present
        if not data.get('user') and not data.get('session_id'):
            raise serializers.ValidationError(
                {'user': 'A user or session must be associated with the cart.'})

        # Discount code validation (if used)
        if data.get('discount_code') and len(data['discount_code']) > 50:
            raise serializers.ValidationError(
                {'discount_code': 'Discount code cannot exceed 50 characters.'})

        return data
