from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Cart, CartItem, CustomUser, Product, Category, Reviews
from .serializers import CartItemSerializer, CartSerializer, CategoryDetailSerializer, CategoryListSerializer, ProductListSerializer, ProductDetailSerializer, ReviewSerializer




User = get_user_model()

@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(featured=True)
    serializer =  ProductListSerializer(products, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)



@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')
    product_id = request.data.get('product_id')

    cart, _ = Cart.objects.get_or_create(cart_code=cart_code)
    product, _ =  Product.objects.get_or_create(id=product_id)
    cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cartitem.quantity += 1

    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('cartitem_id')
    quantity = int(request.data.get('quantity'))

    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({"data": serializer.data, "message": "Cart item updated successfully."})



@api_view(['POST'])
def add_review(request):
    product_id = request.data.get('product_id')
    email = request.data.get('email')
    rating= request.data.get('rating')
    comment = request.data.get('comment')


    product = Product.objects.get(id=product_id)
    user = User.objects.get(email=email)

    if Reviews.objects.filter(product=product, user=user).exists():
        return Response({"error": "You already dropped a review for this product"}, status=400)

    review = Reviews.objects.create(
        product=product,
        user=user,
        rating=rating,
        comment=comment
    )

    serializer = ReviewSerializer(review)
    return Response({"data": serializer.data, "message": "Review added successfully."})


@api_view(['PUT'])
def update_review(request, pk):
    review = Reviews.objects.get(id=pk) 
    rating = request.data.get("rating")
    comment_text = request.data.get("comment")

    review.rating = rating 
    review.comment = comment_text
    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_review(request, pk):
    review = Reviews.objects.get(id=pk) 
    review.delete()

    return Response("Review deleted successfully!", status=204)