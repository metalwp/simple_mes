import re
import os

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from apps.process_manager.models import ProcessStep
from apps.account.models import Menu

register = template.Library()


def get_structure_data(request):
    """处理菜单结构"""
    menu = request.session[settings.SESSION_MENU_KEY]
    # print("menu", menu)
    all_menu = menu[settings.ALL_MENU_KEY]
    # print("all_menu", all_menu)
    permission_url = menu[settings.PERMISSION_MENU_KEY]
    # for url in permission_url:
    #     print(url)


    # 定制数据结构
    all_menu_dict = {}
    all_menu_list = []
    for item in all_menu:
        item['status'] = False
        item['open'] = False
        item['children'] = []
        # all_menu_dict[item['id']] = item

    for permission in permission_url:
        for item in all_menu:
            if permission['menu_id'] == item['id']:
                item['url'] = permission['url']
                item['status'] = True
                break
    all_menu_copy = all_menu[:]
    for m in all_menu_copy:
        for item in all_menu:
            if m['parent_id'] == item['id'] and m['status']:
                item['status'] = True
                item['url'] = '#'

    # for menu in all_menu:
    #     print(menu)

    request_url = request.path_info
    for item in all_menu:
        if item.get('url'):
            if re.match(item.get('url'), request_url):
                item['open'] = True

    while all_menu:
        item = all_menu[0]
        if not item['parent_id']:
            all_menu_list.append(item)
            all_menu.remove(item)
        else:
            for menu in all_menu_list:
                if item['parent_id'] == menu['id']:
                    menu['children'].append(item)
                    all_menu.remove(item)

    return all_menu_list


def get_menu_html(menu_data):
    """显示：菜单 + [子菜单] + 权限(url)"""
    # for menu in menu_data:
    #     print(menu['id'], menu['title'], menu['parent_id'], menu['status'],)
    #     if menu['children']:
    #         for child in menu['children']:
    #             print(child)
    option_str1 = """
        <li><a href="{url}"><i class="{icon}"></i> <span>{title}</span></a></li>
    """

    option_str2 = """
        <li class="treeview">
          <a href="{url}"><i class="{icon}"></i> <span>{title}</span>
            <span class="pull-right-container">
                <i class="fa fa-angle-left pull-right"></i>
              </span>
          </a>
          <ul class="treeview-menu">
            {children}
          </ul>
        </li>
    """

    option_str3 = """
        <li><a href="{url}">{title}</a></li>
    """

    menu_html = ''
    for item in menu_data:
        if not item['status']:  # 如果用户权限不在某个菜单下，即item['status']=False, 不显示
            continue
        else:
            if not item['children']:
                menu_html += option_str1.format(url=item['url'],
                                                icon=item['icon'],
                                                title=item['title'])
            else:
                sub_menu = ''
                for child in item['children']:
                    if child['status']:
                        sub_menu += option_str3.format(url=child['url'],
                                                   title=child['title'])
                menu_html += option_str2.format(url=item['url'],
                                                icon=item['icon'],
                                                title=item['title'],
                                                children=sub_menu)
    return menu_html


@register.simple_tag
def rbac_menu(request):
    """
    显示多级菜单：请求过来 -- 拿到session中的菜单，权限数据 -- 处理数据 -- 作显示
    返回多级菜单：数据处理部分抽象出来由单独的函数处理；渲染部分也抽象出来由单独函数处理
    :param request:
    :return:
    """
    menu_data = get_structure_data(request)
    menu_html = get_menu_html(menu_data)

    return mark_safe(menu_html)
    # 因为标签无法使用safe过滤器，这里用mark_safe函数来实现


@register.simple_tag
def rbac_css():
    """
    rabc要用到的css文件路径，并读取返回；注意返回字符串用mark_safe，否则传到模板会转义
    :return:
    """
    css_path = os.path.join('apps/account', 'style_script', 'rbac.css')
    css = open(css_path, 'r', encoding='utf-8').read()
    return mark_safe(css)


@register.simple_tag
def rbac_js():
    """
    rabc要用到的js文件路径，并读取返回
    :return:
    """
    js_path = os.path.join('apps/account', 'style_script', 'rbac.js')
    js = open(js_path, 'r', encoding='utf-8').read()
    return mark_safe(js)

