from django.shortcuts import render
from django.conf import settings
import stripe
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from .models import Cart, CartItem, CustomUser, Order, OrderItem, Product, Category, Reviews, Wishlist
from .serializers import CartItemSerializer, CartSerializer, CategoryDetailSerializer, CategoryListSerializer, OrderSerializer, ProductListSerializer, ProductDetailSerializer, ReviewSerializer, UserSerializer, WishlistSerializer

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt



stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET


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


@api_view(['DELETE'])
def delete_cartitem(request, pk):
    cartitem = CartItem.objects.get(id=pk) 
    cartitem.delete()

    return Response("Cartitem deleted successfully!", status=204)


@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get("email")
    product_id = request.data.get("product_id")

    user = User.objects.get(email=email)
    product = Product.objects.get(id=product_id) 

    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()
        return Response("Wishlist deleted successfully!", status=204)

    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)



@api_view(['GET'])
def product_search(request):
    query = request.query_params.get('query')

    if not query:
        return Response(({"error": "Please provide a search query"}), status=400)
    products = Product.objects.filter(Q(name__icontains=query)| Q(description__icontains=query)| Q(category__name__icontains=query))
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")
    cart = Cart.objects.get(cart_code=cart_code)
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email= email,
            payment_method_types=['card'],


            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name},
                        'unit_amount': int(item.product.price * 100), 
                    },
                    'quantity': item.quantity,
                }
                for item in cart.cartitems.all()
            ] + [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'VAT Fee'},
                        'unit_amount': 500,  # $5 in cents
                    },
                    'quantity': 1,
                }
            ],


           
            mode='payment',
            success_url="https://sites.google.com/view/alx-nexus-success-page/home",
            cancel_url="https://sites.google.com/view/alx-nexus-success-page/failed",
            metadata = {"cart_code": cart_code}
        )
        return Response({'data': checkout_session})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    print("Webhook received:", )

    if sig_header is None:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] in [
        'checkout.session.completed',
        'checkout.session.async_payment_succeeded'
    ]:
        print("Payment succeeded event received")
        session = event['data']['object']
        cart_code = session.get("metadata", {}).get("cart_code")
        fulfill_checkout(session, cart_code)

    return HttpResponse(status=200)



def fulfill_checkout(session, cart_code):
    print("Fulfilling order for session:")
    
    order = Order.objects.create(stripe_checkout_id=session["id"],
        amount=session["amount_total"],
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid")
    

    print(session)


    cart = Cart.objects.get(cart_code=cart_code)
    cartitems = cart.cartitems.all()

    for item in cartitems:
        orderitem = OrderItem.objects.create(order=order, product=item.product, 
                                             quantity=item.quantity)
    

    # Clear the cart after order is created
    cart.delete()


@api_view(['GET'])
def list_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_orders_by_email(request, email):
    orders = Order.objects.filter(customer_email=email).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_user(request):
    username = request.data.get("username")
    email = request.data.get("email")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    profile_picture_url = request.data.get("profile_picture_url")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "username and password are required"}, status=400)
    

    new_user = User.objects.create_user(username=username, email=email,
                                       first_name=first_name, last_name=last_name, password=password)
    
    new_user.profile_picture_url = profile_picture_url
    new_user.save()

    serializer = UserSerializer(new_user)
    return Response(serializer.data)




@api_view(["GET"])
def existing_user(request, email):
    try:
        User.objects.get(email=email)
        return Response({"exists": True}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"exists": False}, status=status.HTTP_404_NOT_FOUND)