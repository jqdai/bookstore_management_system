from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages

from .forms import *
from .models import *
from django.views import generic


@login_required
def index(request):
    '''
    朴实无华且枯燥的主页
    :param request:
    :return:
    '''
    num_books = Book.objects.all().count()
    num_transactions = Transaction.objects.all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    ct = {'num_books': num_books, 'num_transactions': num_transactions, 'num_visits': num_visits}
    return render(request, 'index.html', context=ct)


@login_required
def book_list(request):
    '''
    查看所有库存图书，也可根据一定要求检索
    :param request:
    :return:
    '''
    all_books = Book.objects.all()
    ct = {'all_books': all_books}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data['ISBN']
            bname = form.cleaned_data['name']
            aname = form.cleaned_data['author']
            lang = form.cleaned_data['language']
            pub = form.cleaned_data['publisher']
            publisher = Publisher.objects.get(name=pub)
            selected_books = publisher.book_set.order_by('name')
            if isbn:
                selected_books = selected_books.filter(ISBN=isbn)
            if bname:
                selected_books = selected_books.filter(name=bname)
            if aname:
                aname_list = aname.split('，')
                for name in aname_list:
                    selected_books = selected_books.filter(author__contains=name)
            if lang:
                selected_books = selected_books.filter(language=lang)
            if pub:
                selected_books = selected_books.filter(publisher=pub)
            context = {'selected_books': selected_books}
            return render(request, 'bookstore/search.html', context=context)
    return render(request, 'bookstore/book_list.html', context=ct)


@login_required
def transactions(request):
    '''
    查看所有交易记录，也可根据一定要求检索
    :param request:
    :return:
    '''
    transactions = Transaction.objects.all()
    ct = {'transactions': transactions}
    if request.method == 'POST':
        form = TimeSpanForm(request.POST)
        if form.is_valid():
            stime = form.cleaned_data['start_time']
            etime = form.cleaned_data['end_time']
            selected_trans = Transaction.objects.filter(time__range=(stime, etime))
            context = {'selected_trans': selected_trans}
            return render(request, 'bookstore/time_span.html', context=context)
    return render(request, 'bookstore/transaction_list.html', context=ct)


@login_required
def related_transaction(request, bid):
    '''
    查看某本书的交易记录
    :param request:
    :param bid:
    :return:
    '''
    # try:
    #   book_id = Book.objects.get(pk=pk)
    # except Book.DoesNotExist:
    #   raise Http404("Book does not exist")
    # book = get_object_or_404(Book, book_id=bid)
    book = Book.objects.get(id=bid)
    related_transaction = book.transaction_set.order_by('-time')
    ct = {'book': book, 'related_transaction': related_transaction}
    return render(request, 'bookstore/related_transaction.html', context=ct)


@login_required
def profile(request, uid):
    '''
    查看管理员个人信息
    :param request:
    :param uid:
    :return:
    '''
    admin = get_object_or_404(Admin, id=uid)
    responsible_transactions = Transaction.objects.filter(ruler=admin)
    return render(request, 'bookstore/profile.html', {'admin': admin, 'res_trans': responsible_transactions})


@login_required
def profile_update(request, uid):
    '''
    更新管理员个人信息
    :param request:
    :param uid:
    :return:
    '''
    user = get_object_or_404(User, id=uid)
    admin = get_object_or_404(Admin, user=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            admin.name = form.cleaned_data['name']
            admin.age = form.cleaned_data['age']
            admin.gender = form.cleaned_data['gender']
            admin.phone = form.cleaned_data['phone']
            admin.address = form.cleaned_data['address']
            admin.save()
            return HttpResponseRedirect(reverse('profile', args=[user.id]))
    else:
        default_data = {'name': admin.name, 'age': admin.age, 'gender': admin.gender,
                        'phone': admin.phone, 'address': admin.address}
        form = ProfileForm(default_data)
    return render(request, 'bookstore/profile_update.html', {'form': form, 'user': user})


@login_required
def new_book(request):
    '''
    新书上架
    :param request:
    :return:
    '''
    user = request.user
    if request.method == 'POST':
        form = NewBookForm(request.POST)
        if form.is_valid():
            publisher = Publisher.objects.get(name=form.cleaned_data['publisher'])
            if not publisher:
                publisher = Publisher(name=form.cleaned_data['publisher'])
                publisher.save()
            new_book = Book(
                ISBN=form.cleaned_data['ISBN'],
                name=form.cleaned_data['name'],
                author=form.cleaned_data['author'],
                lang=form.cleaned_data['language'],
                publisher=publisher,
                price=form.cleaned_data['price'],
                inventory=form.cleaned_data['amount'],
            )
            new_book.save()

            new_trans = Transaction(
                in_out='进货',
                book=new_book,
                ruler=user,
                cost=form.cleaned_data['cost'],
                amount=form.cleaned_data['amount'],
                time=timezone.now(),
                paid='已付款',
            )
            new_trans.save()
            messages.error(request, '新书上架成功')
            return HttpResponseRedirect(reverse('transactions'))
        else:
            messages.error(request, '信息填写有误，请重试')
    else:
        default_data = {}
        form = NewBookForm(default_data)
    return render(request, 'bookstore/new_book.html', {'form': form, 'user': user})


@login_required
def add_book(request, bid):
    '''
    已有图书补充库存
    :param request:
    :param bid:
    :return:
    '''
    user = request.user
    targ = Book.objects.get(id=bid)
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            book_amount = form.cleaned_data['amount']
            book_cost = form.cleaned_data['cost']
            targ.save()

            new_trans = Transaction(
                in_out='进货',
                book=targ,
                ruler=user,
                cost=book_cost,
                amount=book_amount,
                time=timezone.now(),
                paid='未付款',
            )
            new_trans.save()
            messages.error(request, '进货成功')
            return HttpResponseRedirect(reverse('transactions'))
        else:
            messages.error(request, '信息填写有误，请重试')
    else:
        default_data = {}
        form = AddForm(default_data)
    return render(request, 'bookstore/add_book.html', {'form': form,'book': targ, 'user': user})


@login_required
def sell_book(request, bid):
    '''
    图书销售
    :param request:
    :param bid:
    :return:
    '''
    user = request.user
    targ = Book.objects.get(id=bid)
    if request.method == 'POST':
        form = SellForm(request.POST)
        if form.is_valid():
            book_amount = form.cleaned_data['amount']
            invent = targ.inventory
            if book_amount <= invent:
                targ.inventory -= book_amount
                targ.save()

                new_trans = Transaction(
                    in_out='出货',
                    book=targ,
                    ruler=user,
                    cost=targ.price,
                    amount=book_amount,
                    time=timezone.now(),
                    paid=True,
                )
                new_trans.save()
                messages.error(request, '出售成功')
                return HttpResponseRedirect(reverse('related_transaction', args=[bid]))
            else:
                messages.error(request, '交易量超过库存，请重试')
    return render(request, 'bookstore/sell_book.html', {'form': SellForm(), 'book': targ, 'user': user})


@login_required
def edit_book(request, bid):
    '''
    修改图书信息
    :param request:
    :param bid:
    :return:
    '''
    user = request.user
    targ = get_object_or_404(Book, id=bid)
    if request.method == 'POST':
        form = EditBookForm(request.POST)
        if form.is_valid():
            publisher = Publisher.objects.get(name=form.cleaned_data['publisher'])
            if not publisher:
                publisher = Publisher(name=form.cleaned_data['publisher'])
                publisher.save()
            targ.name = form.cleaned_data['name']
            targ.author = form.cleaned_data['author']
            targ.language = form.cleaned_data['language']
            targ.publisher = publisher
            targ.price = form.cleaned_data['price']
            targ.save()
            messages.error(request, '修改成功')
            return HttpResponseRedirect(reverse('related_transaction', args=[bid]))
        else:
            messages.error(request, '修改失败，请重试。注意务必按照规定的格式填写信息！')
    else:
        default_data = {'name': targ.name, 'author': targ.author, 'publisher': targ.publisher,
                        'language': targ.language, 'price': targ.price}
        form = EditBookForm(default_data)
    return render(request, 'bookstore/edit_book.html', {'form': form, 'book': targ, 'user': user})


@login_required
def payment(request):
    '''
    为未付款订单付款或退货
    :param request:
    :return:
    '''
    user = request.user
    unpaid_transactions = Transaction.objects.filter(paid='未付款')
    error_msg = ''
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            tid = form.cleaned_data['tid']
            tpaid = form.cleaned_data['paid']
            trans = unpaid_transactions.get(id=tid)
            if trans:
                trans.paid = tpaid
                if tpaid == '已付款':
                    trans.book.inventory += trans.amount
                    messages.error(request, '付款成功')
                else:
                    messages.error(request, '退货成功')
                trans.save()
                trans.book.save()
                return HttpResponseRedirect(reverse('transactions'))
            else:
                messages.error(request, '该订单不存在，或已付款或退货')
    ct = {'form': PayForm(), 'up_trans': unpaid_transactions, 'user': user}
    return render(request, 'bookstore/payment.html', context=ct)


@login_required
def publishers(request):
    '''
    查看所有出版社，也可根据一定要求检索
    :param request:
    :return:
    '''
    pubs = Publisher.objects.all()
    ct = {'pubs': pubs}
    if request.method == 'POST':
        form = PubSearchForm(request.POST)
        if form.is_valid():
            pub_name = form.cleaned_data['name']
            selected_pubs = Publisher.objects.filter(name__contains=pub_name)
            context = {'selected_pubs': selected_pubs}
            return render(request, 'bookstore/pub_search.html', context=context)
    return render(request, 'bookstore/publisher_list.html', context=ct)


@login_required
def pub_books(request, pid):
    '''
    展示出版社基本信息与所出版图书，可以修改基本信息
    :param request:
    :param pid:
    :return:
    '''
    publisher = get_object_or_404(Publisher, id=pid)
    published_books = publisher.book_set.filter(publisher=publisher)
    return render(request, 'bookstore/pub_books.html', {'publisher': publisher, 'published_books': published_books})


@login_required
def pub_update(request, pid):
    user = request.user
    publisher = get_object_or_404(Publisher, id=pid)
    if request.method == 'POST':
        form = PubSearchForm(request.POST)
        if form.is_valid():
            publisher.name = form.cleaned_data['name']
            publisher.save()
            messages.error(request, '修改成功')
            return HttpResponseRedirect(reverse('profile', args=[pid]))
        else:
            messages.error(request, '修改失败，请重试。注意务必按照规定的格式填写信息！')
    else:
        default_data = {'name': publisher.name, }
        form = PubSearchForm(default_data)
    return render(request, 'bookstore/profile_update.html', {'form': form, 'user': user})
