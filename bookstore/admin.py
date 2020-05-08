from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


# admin.site.register(Admin)
# admin.site.register(Book)
# admin.site.register(Transaction)


class AdminInline(admin.StackedInline):
    model = Admin
    can_delete = False
    verbose_name_plural = 'admins'


class UserAdmin(BaseUserAdmin):
    inlines = (AdminInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class TransactionInline(admin.TabularInline):
    model = Transaction


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('name', 'country')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'publisher', 'ISBN', 'price', 'inventory')
    list_filter = ('author', 'publisher')
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'in_out', 'cost', 'amount', 'time')
    list_filter = ('book', 'time')

