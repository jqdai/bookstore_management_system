from django.core import validators as vl
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


class Admin(models.Model):
    """
    管理员信息模式，包括 id、用户名、密码、是否为超级管理员、姓名、性别、年龄、地址、电话号码
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, verbose_name='姓名')
    gender = models.CharField(max_length=1, verbose_name='性别', help_text='请输入“男”或者“女”', validators=
                              [vl.RegexValidator(regex="^['男'|'女']$", message='请确保性别格式正确！')])
    age = models.PositiveIntegerField(verbose_name='年龄',
                                      validators=[vl.MaxValueValidator(99), vl.MinValueValidator(1)], default=18)
    address = models.CharField(max_length=50, verbose_name='住址')
    phone = models.CharField(max_length=11, verbose_name='联系方式（手机）', help_text='请输入中国大陆11位手机号', validators=
                             [vl.RegexValidator(regex='^1(3|5|7|8|9)\d{9}$', message='请确保手机号格式正确！')])

    class Meta:
        verbose_name = '管理员信息'
        verbose_name_plural = '管理员信息'

    def __str__(self):
        return self.user.get_username()


class Publisher(models.Model):
    name = models.CharField(max_length=30, verbose_name='出版社')

    class Meta:
        verbose_name = '出版社'
        verbose_name_plural = '出版社'
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pub_books', args=[str(self.id)])


class Category(models.Model):
    name = models.CharField(max_length=10, verbose_name='类别')

    class Meta:
        verbose_name = '类别'
        verbose_name_plural = '类别'
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cat_books', args=[str(self.id)])


class Author(models.Model):
    name = models.CharField(max_length=30, verbose_name='作者姓名')

    class Meta:
        verbose_name = '作者'
        verbose_name_plural = '作者'
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('author_books', args=[str(self.id)])


class Book(models.Model):
    """
    书籍信息模式，包括 ISBN号、书名、出版社、价格、库存
    """
    ISBN = models.CharField(max_length=13, verbose_name='ISBN号', help_text='请输入纯数字ISBN（不带横杠）', validators=
                            [vl.RegexValidator(regex='^\d{13}$', message='请确保ISBN格式正确！')])
    name = models.CharField(max_length=50, verbose_name='书名')
    language = models.CharField(max_length=10, verbose_name='语言', default='汉语')
    author = models.ManyToManyField(Author, verbose_name='作者')
    publisher = models.ForeignKey(Publisher, on_delete=models.DO_NOTHING, verbose_name='出版社')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='售价', validators=
                                [vl.MaxValueValidator(999.99, message='最高999.99元'),
                                 vl.MinValueValidator(0.01, message='最低0.01元')])
    inventory = models.IntegerField(verbose_name='当前库存', validators=[vl.MinValueValidator(0)], default=0)
    category = models.ManyToManyField(Category, verbose_name='类别')

    class Meta:
        verbose_name = '图书信息'
        verbose_name_plural = '图书信息'
        ordering = ['name', 'publisher', ]

    def __str__(self):
        return '《' + self.name + '》，' + self.get_author() + '，' + self.ISBN + '，' + self.publisher.name

    def get_absolute_url(self):
        return reverse('related_transaction', args=[str(self.id)])

    def get_author(self):
        return '，'.join([a.name for a in self.author.order_by('name')])

    def get_category(self):
        return '，'.join([c.name for c in self.category.order_by('name')])


class Transaction(models.Model):
    """
    交易记录模式，包括 买入卖出、商品 ISBN号、交易价格、交易数量、交易时间、付款状态
    """
    in_out = models.CharField(max_length=2, verbose_name='进货/出货', help_text='请输入“进货”或者“出货”', validators=
                              [vl.RegexValidator(regex=(r'^(?:进货|出货)$'), message='请确保输入“进货”或者“出货”之一！')])
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING, verbose_name='商品')
    ruler = models.ForeignKey(Admin, on_delete=models.DO_NOTHING, verbose_name='执行交易的管理员')
    cost = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='成交金额')
    amount = models.PositiveIntegerField(verbose_name='成交数量',
                                         validators=[vl.MinValueValidator(1), vl.MaxValueValidator(9999)])
    time = models.DateTimeField(auto_now_add=True, verbose_name='成交时间')
    paid = models.CharField(max_length=3, verbose_name='未付款/已付款/已退货', help_text='请输入“未付款“、”已付款“、”已退货“之一',
                            validators=[vl.RegexValidator(regex=(r'^(?:未付款|已付款|已退货)$'),
                                                          message='请确保输入“未付款“、”已付款“、”已退货“之一！')])

    class Meta:
        verbose_name = '交易记录'
        verbose_name_plural = '交易记录'
        ordering = ['-time']

    def __str__(self):
        rt = ''
        rt += 'Book name: ' + self.book.name
        rt += 'Author' + self.book.get_author()
        rt += '\nISBN: ' + self.book.ISBN
        rt += '\nDate: ' + str(self.time)
        rt += '\n' + self.paid
        return rt

    def recent_deal(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.time <= now
