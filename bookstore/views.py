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
            cate = form.cleaned_data['category']
            selected_books = Book.objects.distinct()
            if pub:
                # selected_books = Publisher.objects.get(name=pub).book_set.order_by('name')
                selected_books = Book.objects.filter(publisher__name__contains=pub)
            if isbn:
                selected_books = selected_books.filter(ISBN=isbn)
            if bname:
                selected_books = selected_books.filter(name__contains=bname)
            if aname:
                aname_list = aname.split('，')
                for name in aname_list:
                    selected_books = selected_books.filter(author__name__contains=name)
            if lang:
                selected_books = selected_books.filter(language=lang)
            if cate:
                selected_books = selected_books.filter(category__name__contains=cate)
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
            stat = form.cleaned_data['stat']
            selected_trans = Transaction.objects.filter(time__range=(stime, etime))
            if stat:
                selected_trans = selected_trans.filter(in_out=stat)
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
            admin.address = form.cleaned_data['address']
            admin.phone = form.cleaned_data['phone']
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
    admin = Admin.objects.get(user=user)
    if request.method == 'POST':
        form = NewBookForm(request.POST)
        if form.is_valid():
            pubtemp = Publisher.objects.filter(name=form.cleaned_data['publisher'])
            if not pubtemp:
                publisher = Publisher(name=form.cleaned_data['publisher'])
                publisher.save()
            else:
                publisher = pubtemp[0]
            catetemp = Category.objects.filter(name=form.cleaned_data['category'])
            if not catetemp:
                category = Category(name=form.cleaned_data['category'])
                category.save()
            else:
                category = catetemp[0]
            new_book = Book(
                ISBN=form.cleaned_data['ISBN'],
                name=form.cleaned_data['name'],
                language=form.cleaned_data['language'],
                publisher=publisher,
                category=category,
                price=form.cleaned_data['price'],
                inventory=form.cleaned_data['amount'],
            )
            new_book.save()
            author_list = form.cleaned_data['author'].split('，')
            for aname in author_list:
                auth_temp = Author.objects.filter(name=aname)
                if not auth_temp:
                    new_author = Author(name=aname)
                    new_author.save()
                else:
                    new_author = auth_temp[0]
                new_book.author.add(new_author)

            new_trans = Transaction(
                in_out='进货',
                book=new_book,
                ruler=admin,
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
    admin = Admin.objects.get(user=user)
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
                ruler=admin,
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
    admin = Admin.objects.get(user=request.user)
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
                    ruler=admin,
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
    return render(request, 'bookstore/sell_book.html', {'form': SellForm(), 'book': targ, 'admin':admin})


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
            publishers = Publisher.objects.filter(name=form.cleaned_data['publisher'])
            if not publishers:
                publisher = Publisher(name=form.cleaned_data['publisher'])
                publisher.save()
            else:
                publisher = publishers[0]
            categories = Category.objects.filter(name=form.cleaned_data['category'])
            if not categories:
                category = Category(name=form.cleaned_data['category'])
                category.save()
            else:
                category = categories[0]

            # 修改 author 时，先清除原有的多对多关联，再重新加
            targ.author.clear()
            aname_list = form.cleaned_data['author'].split('，')
            for name in aname_list:
                au = Author.objects.filter(name__contains=name)
                if au:
                    targ.author.add(au[0])
                else:
                    new_author = Author(name=name)
                    new_author.save()
                    targ.author.add(new_author)

            targ.name = form.cleaned_data['name']
            targ.language = form.cleaned_data['language']
            targ.publisher = publisher
            targ.category = category
            targ.price = form.cleaned_data['price']
            targ.save()
            messages.error(request, '修改成功')
            return HttpResponseRedirect(reverse('related_transaction', args=[bid]))
        else:
            messages.error(request, '修改失败，请重试。注意务必按照规定的格式填写信息！')
    else:
        default_data = {'name': targ.name, 'author': targ.get_author(), 'publisher': targ.publisher,
                        'language': targ.language, 'category': targ.category, 'price': targ.price}
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
    查看所有出版社，也可根据名称检索
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
    展示出版社信息与所出版图书，可以修改信息
    :param request:
    :param pid:
    :return:
    '''
    publisher = get_object_or_404(Publisher, id=pid)
    published_books = publisher.book_set.filter(publisher=publisher)
    return render(request, 'bookstore/pub_books.html', {'publisher': publisher, 'published_books': published_books})


@login_required
def pub_update(request, pid):
    '''
    修改出版社信息
    :param request:
    :param pid:
    :return:
    '''
    publisher = get_object_or_404(Publisher, id=pid)
    if request.method == 'POST':
        form = PubUpdateForm(request.POST)
        if form.is_valid():
            publisher.name = form.cleaned_data['name']
            publisher.save()
            messages.error(request, '修改成功')
            return HttpResponseRedirect(reverse('pub_books', args=[pid]))
        else:
            messages.error(request, '修改失败，请重试。注意务必按照规定的格式填写信息！')
    else:
        default_data = {'name': publisher.name, }
        form = PubUpdateForm(default_data)
    return render(request, 'bookstore/pub_update.html', {'form': form, 'publisher': publisher})


@login_required
def authors(request):
    '''
    查看所有作者，也可根据姓名检索
    :param request:
    :return:
    '''
    all_authors = Author.objects.all()
    selected_authors = all_authors
    ct = {'all_authors': all_authors}
    if request.method == 'POST':
        form = AuthorSearchForm(request.POST)
        if form.is_valid():
            aname = form.cleaned_data['name']
            if aname:
                selected_authors = all_authors.filter(name__contains=aname)
            context = {'selected_authors': selected_authors}
            return render(request, 'bookstore/author_search.html', context=context)
    return render(request, 'bookstore/author_list.html', context=ct)


@login_required
def author_books(request, aid):
    '''
    展示作者个人信息与所作图书，可以修改个人信息
    :param request:
    :param pid:
    :return:
    '''
    author = get_object_or_404(Author, id=aid)
    author_books = author.book_set.filter(author=author)
    return render(request, 'bookstore/author_books.html', {'author': author, 'author_books': author_books})


@login_required
def author_update(request, aid):
    '''
    修改作者个人信息
    :param request:
    :param aid:
    :return:
    '''
    author = get_object_or_404(Author, id=aid)
    if request.method == 'POST':
        form = AuthorUpdateForm(request.POST)
        if form.is_valid():
            author.name = form.cleaned_data['name']
            author.save()
            messages.error(request, '修改成功')
            return HttpResponseRedirect(reverse('author_books', args=[aid]))
        else:
            messages.error(request, '修改失败，请重试。注意务必按照规定的格式填写信息！')
    else:
        default_data = {'name': author.name, }
        form = AuthorUpdateForm(default_data)
    return render(request, 'bookstore/author_update.html', {'form': form, 'author': author})


@login_required
def categories(request):
    '''
    查看所有类型，也可根据名称检索
    :param request:
    :return:
    '''
    cats = Category.objects.all()
    ct = {'cats': cats}
    if request.method == 'POST':
        form = CatSearchForm(request.POST)
        if form.is_valid():
            cat_name = form.cleaned_data['name']
            selected_cats = Category.objects.filter(name__contains=cat_name)
            context = {'selected_cats': selected_cats}
            return render(request, 'bookstore/cat_search.html', context=context)
    return render(request, 'bookstore/category_list.html', context=ct)


@login_required
def cat_books(request, cid):
    '''
    展示类型信息与所属图书，可以修改信息
    :param request:
    :param pid:
    :return:
    '''
    cat = get_object_or_404(Category, id=cid)
    cat_books = cat.book_set.filter(category=cat)
    return render(request, 'bookstore/cat_books.html', {'category': cat, 'cat_books': cat_books})


@login_required
def cat_update(request, cid):
    '''
    修改类型信息
    :param request:
    :param pid:
    :return:
    '''
    cat = get_object_or_404(Category, id=cid)
    if request.method == 'POST':
        form = CatUpdateForm(request.POST)
        if form.is_valid():
            cat.name = form.cleaned_data['name']
            cat.save()
            messages.error(request, '修改成功')
            return HttpResponseRedirect(reverse('cat_books', args=[cid]))
        else:
            messages.error(request, '修改失败，请重试。注意务必按照规定的格式填写信息！')
    else:
        default_data = {'name': cat.name, }
        form = CatUpdateForm(default_data)
    return render(request, 'bookstore/cat_update.html', {'form': form, 'cat': cat})

