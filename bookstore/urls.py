from django.urls import path, include
from bookstore import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.book_list, name='books'),
    path('books/<int:bid>/', views.related_transaction, name='related_transaction'),
    path('books/<int:bid>/add/', views.add_book, name='addbook'),
    path('books/<int:bid>/sell/', views.sell_book, name='sellbook'),
    path('books/<int:bid>/edit/', views.edit_book, name='editbook'),
    path('newbook/', views.new_book, name='newbook'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/payment/', views.payment, name='payment'),
    path('publishers/', views.publishers, name='publishers'),
    path('publishers/<int:pid>/', views.pub_books, name='pub_books'),
    path('publishers/<int:pid>/update/', views.pub_update, name='pub_update'),
    path('authors/', views.authors, name='authors'),
    path('authors/<int:aid>/', views.author_books, name='author_books'),
    path('authors/<int:aid>/update/', views.author_update, name='author_update'),
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),
    # path('user/<int:uid>/pwd_reset', views.pwd_reset, name='pwd_reset'),
    path('user/<int:uid>/profile/', views.profile, name='profile'),
    path('user/<int:uid>/profile/update/', views.profile_update, name='profile_update'),
]
