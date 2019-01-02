import hashlib

from django.shortcuts import render
from django.shortcuts import redirect
from login import models
from login.models import User
import time
from django.conf import settings
import datetime


# Create your views here.

def index(request):
    print(request.session.get("is_login") is None)
    if request.session.get("is_login") is None:
        return render(request, 'login/index.html')
    else:
        return redirect('/home')


def login(request):
    if request.session.get("is_login") is True:
        return redirect('/home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        message = "所有字段都是必填"

        if username and password:
            username = username.strip()
            try:
                user = User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['username'] = username
                    return redirect('/home')
                else:
                    message = "密码错误"
            except:
                message = "用户名不存在"
        return render(request, 'login/login.html', {"message": message})
    return render(request, 'login/login.html')


def register(request):
    if request.session.get("is_login") is True:
        return redirect('/home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        sex = request.POST.get('sex')
        message = "所有字段都是必填"

        if username and password and password and email and sex:
            username = username.strip()
            try:
                user = User.objects.get(name=username)
                message = "用户名已存在"
                return render(request, 'login/register.html', {"message": message})
            except:
                creat_user = User()
                creat_user.name = username
                creat_user.password = password
                creat_user.email = email
                creat_user.sex = sex
                creat_user.c_time = time.time()
                print(username)
                creat_user.save()

                code = make_confirm_string(creat_user)
                send_mail(email, code)

                return redirect("/login")
        else:
            return render(request, 'login/register.html', {"message": message})
    return render(request, 'login/register.html')


def logout(request):
    request.session.clear()
    return redirect('/login')


def home(request):
    if request.session.get("is_login") is True:
        return render(request, 'login/home.html', {"username": request.session.get("username")})
    return redirect('/index')


def send_mail(email, code):
    from django.core.mail import EmailMultiAlternatives

    subject = '来自fuyang.com的注册确认邮件'

    text_content = '''感谢注册fuyang.com，如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>fuyang</a>，</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8100', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user, )
    return code


def hash_code(s, salt='mysite'):  # 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def confirm_code(request):
    code = request.GET.get('code')
    print(code)
    try:
        sys_code = models.ConfirmString.objects.get(code=code.strip())
        print(sys_code)

        # user_id = sys_code.user_id
        # user_info = models.User.objects.get(id=user_id)
        # user_info.has_confirmed = True
        # user_info.save()

        sys_code.user.has_confirmed = True
        sys_code.user.save()
        sys_code.delete()

        message = "确认成功"
        return render(request, 'login/confirm_code.html', {"message": message})

    except:
        message = "确认码错误！"
        return render(request, 'login/confirm_code.html', {"message": message})
