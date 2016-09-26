from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.shortcuts import redirect

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    now = datetime.datetime.now()
    visits_cookie = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(now))
    last_visit_time = datetime.datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (now - last_visit_time).days > 0:
        visits = visits_cookie + 1
        request.session['last_vist'] =  str(now)
    else:
        request.session['last_visit'] =  last_visit_cookie
        visits = visits_cookie

    request.session['visits'] = visits

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)
    return response

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=True)
            print(category, category.slug)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


def about(request):
    if request.session.test_cookie_worked():
        print("WORKED!")
        request.session.delete_test_cookie()
    return render(request, 'rango/about.html', {})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.view = 0
                page.save()
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                profile.save()
                registered = True
            else:
                print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered
                  })

def user_login(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            print("Invalid login details: {0}, {1}".format((username, password)))
            return HttpResponse("Invalid login details supplied")
    else:
        return render(request, 'rango/login.html', {})

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse('You are logged in .')
    else:
        return HttpResponse("You are not logged in.")

@login_required
def restricted(request):
    return HttpResponse("you can see text")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def track_url(request):
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
    if page_id:
        try:
            page = Page.objects.get(id=page_id)
            page.views = page.views + 1
            page.save()
            return redirect(page.url)
        except:
            return HttpResponse("Page id {0} not found".format(page_id))
    print("No page_id in get string")
    return redirect(reverse('index'))