from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("product/<str:id>", views.product, name="product"),
    path('addWatchlist', views.AddWatchlist, name="addWatchlist"),
    path('removeWatchlist', views.RemoveWatchlist, name="removeWatchlist"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('addBid', views.addBid, name="addBid"),
    path('close', views.close, name="close"),
    path('comment', views.comment, name='comment'),
    path('categories', views.categories, name='categories')
]
