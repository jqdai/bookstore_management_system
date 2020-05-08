from django.urls import path, include
from bookstore import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.book_list, name='books'),
    path('books/<int:bid>/', views.related_transaction, name='related_transaction'),
    path('books/<int:bid>/add/', views.add_book, name='addbook'),
    path('books/<int:bid>/sell/', views.sell_book, name='sellbook'),
    path('books/<int:bid>/edit/', views.edit_book, name='editbook'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/payment/', views.payment, name='payment'),
    path('newbook/', views.new_book, name='newbook'),
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),
    # path('user/<int:uid>/pwd_reset', views.pwd_reset, name='pwd_reset'),
    path('user/<int:uid>/profile', views.profile, name='profile'),
    path('user/<int:uid>/profile/update/', views.profile_update, name='profile_update'),
]
