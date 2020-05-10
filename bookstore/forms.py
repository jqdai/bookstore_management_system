from django import forms
from django.core import validators as vl
from django.core.exceptions import ValidationError


class ProfileForm(forms.Form):
    '''
    修改管理员个人信
    '''
    sex = (('男', '男'), ('男', '女'))
    name = forms.CharField(label='姓名', max_length=30)
    age = forms.CharField(label='年龄', max_length=2)
    gender = forms.CharField(label='性别', widget=forms.widgets.Select(choices=sex))
    phone = forms.CharField(label='电话', max_length=11,
                            validators=[vl.RegexValidator(regex='^1(3|5|7|8|9)\d{9}$', message='请确保手机号格式正确！')])
    address = forms.CharField(label='住址', max_length=50)


class NewBookForm(forms.Form):
    '''
    新书上架
    '''
    ISBN = forms.CharField(label='ISBN', max_length=13)
    name = forms.CharField(label='书名', max_length=50)
    author = forms.CharField(label='作者', max_length=30)
    language = forms.CharField(label='作者', max_length=10)
    publisher = forms.CharField(label='出版社', max_length=30)
    category = forms.CharField(label='类型', max_length=10)
    cost = forms.DecimalField(label='进价', max_value=999.99, min_value=0.01, max_digits=5, decimal_places=2)
    price = forms.DecimalField(label='零售价', max_value=999.99, min_value=0.01, max_digits=5, decimal_places=2)
    amount = forms.IntegerField(label='数量', min_value=1)
    summary = forms.CharField(label='简介', max_length=100)


class SellForm(forms.Form):
    '''
    图书销售
    '''
    amount = forms.IntegerField(label='数量', min_value=1)


class AddForm(forms.Form):
    '''
    已有图书补充库存
    '''
    amount = forms.IntegerField(label='数量', min_value=1)
    cost = forms.DecimalField(label='进价', max_value=999.99, min_value=0.01, max_digits=5, decimal_places=2)


class SearchForm(forms.Form):
    '''
    按一定要求检索库存图书
    '''
    ISBN = forms.CharField(label='ISBN', max_length=13, required=False)
    name = forms.CharField(label='书名', max_length=50, required=False)
    author = forms.CharField(label='作者', max_length=30, required=False)
    language = forms.CharField(label='作者', max_length=10, required=False)
    publisher = forms.CharField(label='出版社', max_length=30, required=False)
    category = forms.CharField(label='类型', max_length=10, required=False)


class TimeSpanForm(forms.Form):
    '''
    按时间范围检索交易记录
    '''
    states = (('in', '进货'), ('out', '出货'))
    start_time = forms.DateTimeField(label='起始时间')
    end_time = forms.DateTimeField(label='结束时间')
    stat = forms.CharField(label='进货/出货', widget=forms.widgets.Select(choices=states))


class EditBookForm(forms.Form):
    '''
    编辑图书信息
    '''
    name = forms.CharField(label='书名', max_length=50)
    author = forms.CharField(label='作者', max_length=30)
    publisher = forms.CharField(label='出版社', max_length=30)
    language = forms.CharField(label='作者', max_length=10)
    price = forms.DecimalField(label='零售价', max_value=999.99, min_value=0.01, max_digits=5, decimal_places=2)
    category = forms.CharField(label='类型', max_length=10)
    summary = forms.CharField(label='简介', max_length=100)


class PayForm(forms.Form):
    '''
    为未付款订单付款或退货
    '''
    states = (('pay', '已付款'), ('ret', '已退货'))
    tid = forms.IntegerField(label='订单编号')
    paid = forms.CharField(label='付款状态', widget=forms.widgets.Select(choices=states))


class PubSearchForm(forms.Form):
    name = forms.CharField(label='出版社名称', max_length=30, required=False)


class PubUpdateForm(forms.Form):
    name = forms.CharField(label='出版社名称', max_length=30)


class AuthorSearchForm(forms.Form):
    name = forms.CharField(label='作者姓名', max_length=50, required=False)


class AuthorUpdateForm(forms.Form):
    name = forms.CharField(label='作者姓名', max_length=50)


class CatSearchForm(forms.Form):
    name = forms.CharField(label='类型名称', max_length=10, required=False)


class CatUpdateForm(forms.Form):
    name = forms.CharField(label='类型名称', max_length=10)

