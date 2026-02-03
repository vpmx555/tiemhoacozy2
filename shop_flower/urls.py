from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),

    path("cart/get/", views.get_cart),
    path("cart/add/<int:flower_id>/", views.add_to_cart),
    path("cart/update/", views.update_cart),
    path("cart/remove/", views.remove_cart),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:order_id>/pending/", views.order_pending, name="order_pending"),
    path("policy/", views.policy, name="policy"),
    path("blog/", views.blog, name="blog"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    #path("order-success/<int:order_id>/", views.order_success, name="order_success"),

]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
