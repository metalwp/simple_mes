import re
import json

from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings


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
        user = request.user
        if user.is_authenticated:
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
                    total = model.objects.filter_without_isdelete().count()
                    objs = model.objects.filter_without_isdelete().order_by(sort_str)[
                           (pageNumber - 1) * pageSize:(pageNumber) * pageSize]
                else:
                    objs = model.objects.filter_without_isdelete().filter(
                        Q(product_model__name__contains=search_kw)).order_by(sort_str) \
                        [(pageNumber - 1) * pageSize: pageNumber * pageSize]
                    # 获取查询结果的总条数
                    total = model.objects.filter_without_isdelete().filter(
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
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'update':
            ret, errMsg, rows, total = self.update(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'reset':
            ret, errMsg, rows, total = self.reset(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'profile':
            ret, errMsg, rows, total = self.edit_profile(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'password':
            ret, errMsg, rows, total = self.edit_password(request)
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
        model = User
        id = request.POST.get('id')
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            return True, '', [], 0
        except Exception as e:
            return False, str(e), [], 0

    @staticmethod
    def update(request):
        id = request.POST.get('u_idInput')
        username = request.POST.get('u_usernameInput')
        email = request.POST.get('u_emailInput')
        is_active = True if request.POST.get('u_activeInput') == 'on' else False
        roles_id = request.POST.getlist('u_roleSelect')

        # 进行数据校验
        if not all([username]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        # 检验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return False, '邮箱格式不正确！', [], 0

        # 校验用户是否重复
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            # 用户名不存在
            return False, '用户不存在！', [], 0

        # 进行业务处理：进行用户注册
        user.username = username
        user.email = email
        user.is_active = is_active
        user.roles.clear()
        for id in roles_id:
            r = Role.objects.get(id=id)
            user.roles.add(r)
        user.save()

        return True, '', [], 0

    @staticmethod
    def reset(request):
        id = request.POST.get("id")
        print(request.POST.get("id"))
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            # 用户名不存在
            return False, '用户不存在！', [], 0

        # 进行业务处理：进行用户注册
        user.set_password(settings.DEFAULT_PASSWORD)
        user.save()

        return True, '', [], 0

    @staticmethod
    def edit_profile(request):
        id = request.POST.get('_idInput')
        username = request.POST.get('_usernameInput')
        email = request.POST.get('_emailInput')
        # 进行数据校验
        if not all([username]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        # 检验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return False, '邮箱格式不正确！', [], 0

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            # 用户名不存在
            return False, '用户不存在！', [], 0

        user.username = username
        user.email = email
        user.save()
        return True, '', [], 0

    @staticmethod
    def edit_password(request):

        id = request.POST.get('p_idInput')
        o_pwd = request.POST.get('o_pwdInput')
        n_pwd = request.POST.get('n_pwdInput')
        r_pwd = request.POST.get('r_pwdInput')

        # 进行数据校验
        if not all([o_pwd, n_pwd, r_pwd]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        # 检验密码
        if n_pwd != r_pwd:
            return False, '两次输入的密码不同！', [], 0

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            # 用户名不存在
            return False, '用户不存在！', [], 0
        if user.check_password(o_pwd):
            user.set_password(n_pwd)
            user.save()
            return True, '', [], 0
        else:
            return False, '原密码输入错误！', [], 0


class PermissionView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            model = Permission
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

                    rows.append(
                        {"id": obj.id,
                         'title': obj.title,
                         'URL': obj.url,
                         'menu': obj.menu.title if obj.menu else None,
                         'parent': obj.parent.title if obj.parent else None,
                         })
                return JsonResponse(data)
            else:
                menus = Menu.objects.all()
                permissions = Permission.objects.all()
                return render(request, 'account/permission.html', locals())
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'update':
            ret, errMsg, rows, total = self.update(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def add(request):
        title = request.POST.get('nameInput')
        url = request.POST.get('urlInput')
        menu_id = request.POST.get('menuSelect')
        parent_id = request.POST.get('parentSelect')
        # 进行数据校验
        if not all([title, url]):
            # 数据不完整
            return False, '数据不完整！', [], 0
        if parent_id:
            try:
                parent = Permission.objects.get(id=parent_id)
            except Exception as e:
                return False, '数据错误！', [], 0
        else:
            parent = None
        try:
            permision = Permission.objects.get(title=title)
        except Permission.DoesNotExist:
            permision = None
        if permision:
            return False, '该权限名称已使用！', [], 0
        if menu_id:
            try:
                menu = Menu.objects.get(id=menu_id)
            except Menu.DoesNotExist:
                return False, '菜单选择有误！', [], 0
        else:
            menu = None
        Permission.objects.create(title=title, url=url, menu=menu, parent=parent)
        return True, '', [], 0

    @staticmethod
    def delete(request):
        model = Permission
        id = request.POST.get('id')
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            return True, '', [], 0
        except Exception as e:
            return False, str(e), [], 0

    @staticmethod
    def update(request):
        id = request.POST.get('u_idInput')
        title = request.POST.get('u_nameInput')
        url = request.POST.get('u_urlInput')
        menu_id = request.POST.get('u_menuSelect')
        parent_id = request.POST.get('u_parentSelect')

        if parent_id:
            try:
                parent = Permission.objects.get(id=parent_id)
            except Exception as e:
                return False, '数据错误！', [], 0
        else:
            parent = None

        if menu_id:
            try:
                menu = Menu.objects.get(id=menu_id)
            except Menu.DoesNotExist:
                return False, '菜单选择有误！', [], 0
        else:
            menu = None

        # 进行数据校验
        if not all([id, title, url]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        try:
            obj = Permission.objects.get(id=id)
        except Permission.DoesNotExist:
            return False, '未找到该项权限！', [], 0
        obj.title = title
        obj.url = url
        obj.menu = menu
        obj.parent = parent
        obj.save()
        return True, '', [], 0


class RoleView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            model = Role
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
                    permissions = []
                    for o in obj.permissions.all():
                        permissions.append(o.title)
                    rows.append(
                        {"id": obj.id,
                         "title": obj.title,
                         'permissions': permissions,
                         })
                return JsonResponse(data)
            else:
                permissions = Permission.objects.all()
                return render(request, 'account/role.html', locals())
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'update':
            ret, errMsg, rows, total = self.update(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def add(request):
        title = request.POST.get('titleInput')
        permission_ids = request.POST.getlist('permissionSelect')
        # 进行数据校验
        if not all([title]):
            # 数据不完整
            return False, '数据不完整！', [], 0
        try:
            role = Role.objects.get(title=title)
        except Role.DoesNotExist:
            role = None
        if role:
            return False, '该角色名称已使用！', [], 0

        role = Role.objects.create(title=title)

        if permission_ids:
            for id in permission_ids:
                p = Permission.objects.get(id=id)
                role.permissions.add(p)
        return True, '', [], 0

    @staticmethod
    def delete(request):
        model = Role
        id = request.POST.get('id')
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            return True, '', [], 0
        except Exception as e:
            return False, str(e), [], 0

    @staticmethod
    def update(request):
        id = request.POST.get('u_idInput')
        title = request.POST.get('u_titleInput')
        permission_ids = request.POST.getlist('u_permissionSelect')

        # 进行数据校验
        if not all([id, title]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        try:
            obj = Role.objects.get(id=id)
        except Role.DoesNotExist:
            return False, '未找到该项权限！', [], 0

        obj.permissions.clear()
        for id in permission_ids:
            p = Permission.objects.get(id=id)
            obj.permissions.add(p)

        obj.title = title
        obj.save()
        return True, '', [], 0


class MenuView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            model = Menu
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
                    rows.append(
                        {"id": obj.id,
                         "title": obj.title,
                         'icon': obj.icon,
                         'parent': obj.parent.title if obj.parent else None,
                         })
                return JsonResponse(data)
            else:
                menus = Menu.objects.all()
                return render(request, 'account/menu.html', locals())
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request):
        if request.path.split('/')[-2] == 'add':
            ret, errMsg, rows, total = self.add(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'delete':
            ret, errMsg, rows, total = self.delete(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})
        elif request.path.split('/')[-2] == 'update':
            ret, errMsg, rows, total = self.update(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def add(request):
        title = request.POST.get('titleInput')
        icon = request.POST.get('iconInput')
        parent_id = request.POST.get('parentSelect')
        # 进行数据校验
        if not all([title]):
            # 数据不完整
            return False, '数据不完整！', [], 0
        if parent_id:
            try:
                parent = Menu.objects.get(id=parent_id)
            except Menu.DoesNotExist:
                return False, '无此父菜单！', [], 0
        else:
            parent = None
        try:
            menu = Menu.objects.get(title=title)
        except Menu.DoesNotExist:
            menu = None
        if menu:
            return False, '该菜单名称已使用！', [], 0

        Menu.objects.create(title=title, icon=icon if icon else None, parent=parent)

        return True, '', [], 0

    @staticmethod
    def delete(request):
        model = Menu
        id = request.POST.get('id')
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            return True, '', [], 0
        except Exception as e:
            return False, str(e), [], 0

    @staticmethod
    def update(request):
        id = request.POST.get('u_idInput')
        title = request.POST.get('u_titleInput')
        icon = request.POST.get('u_iconInput')
        parent_id = request.POST.get('u_parentSelect')

        # 进行数据校验
        if not all([id, title]):
            # 数据不完整
            return False, '数据不完整！', [], 0

        if parent_id:
            try:
                parent = Menu.objects.get(id=parent_id)
            except Menu.DoesNotExist:
                return False, '无此父菜单！', [], 0
        else:
            parent = None

        try:
            obj = Menu.objects.get(id=id)
        except Role.DoesNotExist:
            return False, '未找到该菜单！', [], 0

        obj.title = title
        obj.icon = icon if icon else None
        obj.parent = parent
        obj.save()
        return True, '', [], 0


class RolePermissionView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            if request.path.split('/')[-2] == 'getRole':
                model = Role
                total = model.objects.all().count()
                objs = model.objects.all()
                rows = []
                for obj in objs:
                    rows.append(
                        {"id": obj.id,
                         "title": obj.title,
                         })
                return JsonResponse(rows, safe=False)
            elif request.path.split('/')[-2] == 'getPermission':
                model = Permission
                total = model.objects.all().count()
                objs = model.objects.all()
                rows = []
                for obj in objs:
                    rows.append(
                        {"id": obj.id,
                         "pid": obj.parent.id if obj.parent else None,
                         'title': obj.title,
                         'URL': obj.url,
                         'menu': obj.menu.title if obj.menu else None,
                         })
                return JsonResponse(rows, safe=False)

            else:
                menus = Menu.objects.all()
                return render(request, 'account/role_permission.html', locals())
        else:
            request.session['errMsg'] = '请先登陆！'
            return redirect(reverse('account:login'))

    def post(self, request):
        if request.path.split('/')[-2] == 'getChecked':
            ret, errMsg, rows, total, info = self.getChecked(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total, "info": info})
        elif request.path.split('/')[-2] == 'updatePermission':
            ret, errMsg, rows, total = self.updatePermission(request)
            return JsonResponse({"ret": ret, "errMsg": errMsg, "rows": rows, "total": total})

    @staticmethod
    def getChecked(request):
        data = json.loads(request.body)
        role_id = data.get('id')
        permission_list = []
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return False, '未找到此角色！', [], 0, permission_list
        permissons = role.permissions.all()
        for p in permissons:
            permission_list.append(p.id)
        return True, '', [], 0, permission_list

    @staticmethod
    def updatePermission(request):
        data = json.loads(request.body)
        id_list = data.get('idList')
        role_id = data.get('role_id')
        if id_list is None:
            return False, '错误,idList为None！', [], 0
        permission_list = []
        if id_list:
            for id in id_list:
                try:
                    p = Permission.objects.get(id=id)
                    permission_list.append(p)
                except Permission.DoesNotExist:
                    return False, '未找到这个权限，id为'+str(id), [], 0
        if not role_id:
            return False, '请选择角色', [], 0
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return False, '未找到这个角色', [], 0
        role.permissions.clear()
        for p in permission_list:
            role.permissions.add(p)
        return True, '', [], 0






