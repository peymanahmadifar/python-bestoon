from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from .models import Token, Expense, Income, User, Passwordresetcodes
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from .utils import grecaptcha_verify, RateLimited
import random
import string

random_str = lambda N: ''.join(
    random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))


def index(request):
    context = {}
    return render(request, 'index.html', context)

def register(request):
    if 'requestcode' in request.POST:
        if not grecaptcha_verify(request):
            context = {'message': 'کد امنیتی نادرست می‌باشد.'}
            return render(request, 'register.html', context)

        if User.objects.filter(email=request.POST['email']).exists():
            context = {'message': 'forget pass'}
            return render(request, 'register.html', context)

        if not User.objects.filter(username=request.POST['username']).exists():
            code = random_str(28)
            now = timezone.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(email=email, username=username, time=now, code=code, password=password)
            temporarycode.save()
            message = 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'
            message = 'قدیم ها ایمیل فعال سازی می فرستادیم ولی الان شرکتش ما رو تحریم کرده (: پس راحت و بی دردسر'
            body = " برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: <a href=\"{}?code={}\">لینک رو به رو</a> ".format(
                request.build_absolute_uri('/accounts/register/'), code)
            message = message + body
            context = {
                'message': message}
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
    elif 'code' in request.GET:  # user clicked on code
            code = request.GET['code']
            if Passwordresetcodes.objects.filter(code=code).exists():
                new_temp_user = Passwordresetcodes.objects.get(code=code)
                newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password,
                                              email=new_temp_user.email)
                this_token = get_random_string(length=48)
                token = Token.objects.create(user=newuser, token=this_token)
                Passwordresetcodes.objects.filter(code=code).delete()
                context = {
                    'message': 'اکانت شما ساخته شد. توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نخواهد شد! جدی!'.format(
                        this_token)}
                return render(request, 'index.html', context)
            else:
                context = {
                    'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
                return render(request, 'register.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)


@csrf_exempt
def submit_expense(request):
    # TODO; validation form
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token)[0]
    if 'date' in request.POST:
        date = request.POST['date']
    else:
        date = timezone.now()
    Expense.objects.create(user=this_user, amount=request.POST['amount'], text=request.POST['text'],
                           date=date)

    return JsonResponse({
        'status': True
    }, encoder=json.JSONEncoder)
    # return HttpResponse('we are here')


@csrf_exempt
def submit_income(request):
    # TODO; validation form
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token)[0]
    if 'date' in request.POST:
        date = request.POST['date']
    else:
        date = timezone.now()
    Income.objects.create(user=this_user, amount=request.POST['amount'], text=request.POST['text'],
                          date=date)

    return JsonResponse({
        'status': True
    }, encoder=json.JSONEncoder)
    # return HttpResponse('we are here')
