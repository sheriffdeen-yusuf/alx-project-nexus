from django.urls import path 

from . import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Ecommerce API",
      default_version='v1',
      description="This API powers a full-featured e-commerce platform that allows users to browse products, manage a shopping cart, place orders, process secure payments, and submit product reviews.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="sheriffdeenyusuf1130@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('products', views.product_list, name='product_list'),
    path('products/<slug:slug>', views.product_detail, name='product_detail'),
    path('categories', views.category_list, name='category_list'),
    path('categories/<slug:slug>', views.category_detail, name='category_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cartitem_quantity/', views.update_cartitem_quantity, name='update_cartitem_quantity'),
    path('add_review/', views.add_review, name='add_review'),
    path("update_review/<int:pk>/", views.update_review, name="update_review"),
    path("delete_review/<int:pk>/", views.delete_review, name="delete_review"),
    path("delete_cartitem/<int:pk>/", views.delete_cartitem, name="delete_cartitem"),
    path("add_to_wishlist/", views.add_to_wishlist, name="add_to_wishlist"),
    path("search", views.product_search, name="search"),
    path('orders/', views.list_orders, name='orders'),

    path("user_orders/<str:email>", views.list_orders_by_email, name="list_orders_by_email"),
    path("create_user/", views.create_user, name="create_user"),
    path("existing_user/<str:email>", views.existing_user, name="existing_user"),


    path("create_checkout_session/", views.create_checkout_session, name="create_checkout_session"),
    path("webhook/", views.my_webhook_view, name="webhook"),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]