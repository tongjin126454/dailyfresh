from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings

from apps.user.models import User
from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
import time


# Create your views here.



def register(request):
    if request.method =='GET':
        return render(request,'dailyfresh/register.html')
    else:
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 数据不完整校验
        if not all([username, password, email]):
            return render(request, 'dailyfresh/register.html', {'errmsg': '数据不完整'})
        # email合法校验
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'dailyfresh/register.html', {'errmsg': '邮箱格式不正确'})
        # 进行协议是否同意校验
        if allow != 'on':
            return render(request, 'dailyfresh/register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'dailyfresh/register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        # 默认is_active 是True，需要修改为False
        user.is_active = 0
        user.save()
        # 返回应答
        return redirect(reverse('goods:index'))

def register_handle(request):
    ''' 进行注册处理'''
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # 数据不完整校验
    if not all([username, password, email]):
        return render(request, 'dailyfresh/register.html', {'errmsg': '数据不完整'})
    # email合法校验
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'dailyfresh/register.html', {'errmsg': '邮箱格式不正确'})
    # 进行协议是否同意校验
    if allow != 'on':
        return render(request, 'dailyfresh/register.html', {'errmsg': '请同意协议'})
    # 校验用户名是否重复
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 用户名不存在
        user = None
    if user:
        # 用户名已存在
        return render(request, 'dailyfresh/register.html', {'errmsg': '用户名已存在'})

    # 进行业务处理: 进行用户注册
    user = User.objects.create_user(username, email, password)
    # 默认is_active 是True，需要修改为False
    user.is_active = 0
    user.save()
    #返回应答
    return redirect(reverse('goods:index'))

class RegisterView(View):

    def get(self,request):



        return render(request, 'dailyfresh/register.html')
    def post(self,request):
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 数据不完整校验
        if not all([username, password, email]):
            return render(request, 'dailyfresh/register.html', {'errmsg': '数据不完整'})
        # email合法校验
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'dailyfresh/register.html', {'errmsg': '邮箱格式不正确'})
        # 进行协议是否同意校验
        if allow != 'on':
            return render(request, 'dailyfresh/register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'dailyfresh/register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        # 默认is_active 是True，需要修改为False
        user.is_active = 0
        user.save()
        # 使用settings.py中的密钥(创建项目的时候随机生成) ， 和过期时间
        # 创建一个TimedJSONWebSignatureSerializer对象
        serializer = Serializer(settings.SECRET_KEY, 3600)
        # 待加密的信息
        info = {'confirm': user.id}
        # 获得加密的结果，注意类型是 bytes
        token = serializer.dumps(info)  # bytes
        token = token.decode()
        send_register_active_email.delay(email, username, token)
        return redirect(reverse('goods:index'))

class ActiveView(View):
    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except Exception as f:
            return HttpResponse('激活信息已过期')

    # 跳转到登录页面
    #     return redirect(reverse('user:login'))

class LoginView(View):

    def get(self,request):
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # 使用模板
        return render(request, 'dailyfresh/login.html', {'username': username, 'checked': checked})
        # return render(request,'dailyfresh/login.html')
    def post(self, request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remmber_pwd = request.POST.get('remmber_pwd')
        # 校验数据
        if not all([username, password]):
            return render(request, 'dailyfresh/login.html', {'errmsg': '数据不完整'})
        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)
                # 获取登录后所要跳转到的地址
                # 默认跳转到首页

                next_url = request.GET.get('next', reverse('goods:index'))
                # 跳转到next_url
                return redirect(next_url)  # HttpResponseRedirect
            else:
                # 用户未激活
                return render(request, 'dailyfresh/login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'dailyfresh/login.html', {'errmsg': '用户名或密码错误'})