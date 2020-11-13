import re

from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse

from apps.account.models import User, Role, Permission, Menu
from apps.account.service.init_permission import init_permission

# Create your views here.


class RegisterView(View):
    """注册"""
    def get(self, request):
        # 显示注册页面
        return render(request, 'account/register.html')

    def post(self, request):
        # 进行注册处理
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        re_pwd = request.POST.get('re_pwd')
        email = request.POST.get('email')

        # 进行数据校验
        if not all([username, password, re_pwd]):
            # 数据不完整
            return render(request, 'account/register.html', {'errMsg': '数据不完整'})

        # 检验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'account/register.html', {'errMsg': '邮箱格式不正确'})

        # 检验密码
        if password != re_pwd:
            return render(request, 'account/register.html', {'errMsg': '两次输入密码不同'})
        # 校验用户是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            return render(request, 'account/register.html', {'errMsg': '用户已存在'})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 1
        user.save()
        # 返回应答,跳转首页
        return redirect(reverse('account:login'))


class LoginView(View):
    """登录"""
    def get(self, request):
        # 显示登录页面
        # 判断是否记住密码
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')  # request.COOKIES['username']
            checked = 'checked'
        else:
            username = ''
            checked = ''
        if request.session.get('errMsg'):
            errMsg = request.session['errMsg']
            del request.session['errMsg']
            return render(request, 'account/login.html', {'username': username, 'checked': checked, 'errMsg': errMsg})
        else:
            return render(request, 'account/login.html', {'username': username, 'checked': checked})

    def post(self, request):
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # remember = request.POST.get('remember')  # on

        # 校验数据
        if not all([username, password]):
            return render(request, 'account/login.html', {'errMsg': '数据不完整'})

        # 业务处理: 登陆校验
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # print("User is valid, active and authenticated")
                login(request, user)  # 登录并记录用户的登录状态

                init_permission(request, user)  # 调用init_permission，初始化权限

                # 获取登录后所要跳转到的地址, 默认跳转首页
                next_url = request.GET.get('next', reverse('index'))

                #  跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 设置cookie, 需要通过HttpReponse类的实例对象, set_cookie
                # HttpResponseRedirect JsonResponse

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                # 回应 response
                return response

            else:
                # print("The passwoed is valid, but the account has been disabled!")
                return render(request, 'account/login.html', {'errMsg': '账户未激活'})
        else:
            return render(request, 'account/login.html', {'errMsg': '用户名或密码错误'})


# /user/logout
class LogoutView(View):
    """退出登录"""
    def get(self, request):
        logout(request)
        return redirect(reverse('account:login'))


class UserView(View):

    def get(self, request):
        model = User
        if request.path.split('/')[-2] == 'get':
            pageSize = int(request.GET.get('pageSize'))
            pageNumber = int(request.GET.get('pageNumber'))
            sortName = request.GET.get('sortName')
            sortOrder = request.GET.get('sortOrder')
            search_kw = request.GET.get('search_kw')
            if sortOrder == 'asc':
                sort_str = sortName
            else:
                sort_str = '-' + sortName

            if not search_kw:
                total = model.objects.all().count()
                objs = model.objects.all().order_by(sort_str)[
                       (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
            else:
                objs = model.objects.all().filter(
                    Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                    [(pageNumber - 1) * pageSize: pageNumber * pageSize]
                # 获取查询结果的总条数
                total = model.objects.all().filter(
                    Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                    [(pageNumber - 1) * pageSize: pageNumber * pageSize].count()
            rows = []
            data = {"total": total, "rows": rows}
            for obj in objs:
                role = []
                for r in obj.roles.all():
                    role.append(r.title)
                rows.append(
                    {"id": obj.id,
                     'username': obj.username,
                     'email': obj.email,
                     'is_super': obj.is_superuser,
                     'is_active': obj.is_active,
                     'role': role})
            return JsonResponse(data)
        else:
            roles = Role.objects.all()
            return render(request, 'account/user.html', locals())

    def post(self, request):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def add(request):
        username = request.POST.get('usernameInput')
        email = request.POST.get('emailInput')
        pwd = request.POST.get('pwdInput')
        repwd = request.POST.get('repwdInput')
        is_active = True if request.POST.get('activeInput') == 'on' else False
        roles_id = request.POST.getlist('roleSelect')

        # 进行数据校验
        if not all([username, pwd, repwd]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        # 检验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return False, '邮箱格式不正确！', [], 0

        # 检验密码
        if pwd != repwd:
            return False, '两次输入密码不同！', [], 0

        # 校验用户是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            return False, '用户已存在！', [], 0

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, pwd)
        user.is_active = is_active
        user.save()

        for id in roles_id:
            r = Role.objects.get(id=id)
            user.roles.add(r)

        return True, '', [], 0

    @staticmethod
    def delete(request):


        return True, '', [], 0


class PermissionView(View):
    def __get__(self, request):
        pass


class RoleView(View):
    def __get__(self, request):
        pass


class MenuView(View):
    def __get__(self, request):
        pass
