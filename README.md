# 🛒 E-Commerce API (Django + DRF + Stripe)

A fully functional **E-Commerce REST API** built with **Django**, **Django REST Framework**, and **Stripe Checkout**.
This backend powers product listings, categories, carts, reviews, orders, payments, and basic user management.

---

## 🚀 Features

### 🔹 **Products & Categories**

- List all products
- View product detail by slug
- List categories
- View category detail by slug
- Product search (keyword-based)

### 🔹 **Cart & Wishlist**

- Add items to cart
- Update cart item quantities
- Delete cart items
- Add items to wishlist

### 🔹 **Reviews**

- Add a review
- Update a review
- Delete a review

### 🔹 **Orders**

- List all orders
- List orders by user email
- Orders are automatically created after Stripe checkout succeeds

### 🔹 **User Management**

- Create a user (no password required—for guest/quick checkout flow)
- Check if a user exists by email

### 🔹 **Stripe Checkout Integration**

- Create Stripe Checkout session
- Handle payment success using webhook
- Store orders + order items
- Clear cart after successful payment

---

## 🧰 Tech Stack

- **Python 3.x**
- **Django 5+**
- **Django REST Framework**
- **Stripe Checkout API**
- **SQLite / PostgreSQL**
- **Swagger / DRF Spectacular (API docs)**

---

## 📦 Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Migrations

```bash
python manage.py migrate
```

### 4. Run Server

```bash
python manage.py runserver
```

---

## 🔌 API Endpoints

All endpoints are prefixed with:

```
/api/
```

---

## 🏷️ **Products**

### List all products

`GET /api/products`

### Product detail

`GET /api/products/<slug:slug>`

---

## 🗂️ **Categories**

### List categories

`GET /api/categories`

### Category detail

`GET /api/categories/<slug:slug>`

---

## 🛒 **Cart**

### Add to cart

`POST /api/add_to_cart/`

### Update cart item quantity

`POST /api/update_cartitem_quantity/`

### Delete cart item

`DELETE /api/delete_cartitem/<int:pk>/`

---

## ⭐ Reviews

### Add review

`POST /api/add_review/`

### Update review

`PUT /api/update_review/<int:pk>/`

### Delete review

`DELETE /api/delete_review/<int:pk>/`

---

## ❤️ Wishlist

### Add item to wishlist

`POST /api/add_to_wishlist/`

---

## 🎯 Search

### Search products

`GET /api/search?query=laptop`

---

## 📦 Orders

### List all orders

`GET /api/orders/`

### List orders by user email

`GET /api/user_orders/<email>`

---

## 👤 Users

### Create user

`POST /api/create_user/`
Payload:

```json
{
  "username": "john",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture_url": "https://example.com/pic.jpg"
}
```

### Check if user exists

`GET /api/existing_user/<email>`

---

## 💳 Stripe Checkout

### Create checkout session

`POST /api/create_checkout_session/`

### Stripe Webhook endpoint

`POST /api/webhook/`

This webhook:

- Verifies Stripe event signature
- Creates `Order` and related `OrderItem`s
- Clears the cart afterward

---

## 🔧 Webhook Order Fulfillment Flow

When Stripe confirms payment:

1. Stripe triggers `checkout.session.completed`
2. Webhook (`/api/webhook/`) receives event
3. Backend:

   - Creates `Order`
   - Creates `OrderItem`s for each cart item
   - Deletes the cart

4. Returns `200 OK` to Stripe

---

## 📘 API Documentation (Swagger)

If using DRF Spectacular:

```
/api/swagger/
/api/redoc/
```

---

## 🗂️ Project Structure

```
api/
 ├── models.py
 ├── views.py
 ├── serializers.py
 ├── urls.py
ecommerceProject/
 ├── settings.py
 ├── urls.py
```

---

## 🛠️ Deployment Notes (Render + Gunicorn)

Gunicorn command:

```
gunicorn ecommerceProject.wsgi:application --bind 0.0.0.0:$PORT
```

Render automatically sets `$PORT`.

---

## 📄 License

MIT License

---
