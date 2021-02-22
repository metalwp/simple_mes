from ..models import User, Menu
from apps.order_manager.models import Order
from apps.process_manager.models import ProcessStep, ProcessStep_MaterialModel, ProcessRoute
from simple_mes import settings


def init_permission(request, user_obj):
    """
    初始化用户权限, 写入session
    :param request:
    :param user_obj:
    :return:
    """
    try:
        order = Order.objects.filter_without_isdelete().get(status=1)
    except Order.DoesNotExist:
        order = None

    step_name_list = []
    if order:
        steps = ProcessStep.objects.filter_without_isdelete().filter(process_route=order.product_model.process_route)
        # print("init_permission")
        # print(user_obj.username)
        step_name_list = [step.name for step in steps]

    # print(step_name_list)

    permission_item_list = user_obj.roles.values('permissions__url',
                                                 'permissions__title',
                                                 'permissions__menu_id').distinct()
    # for permission_item in permission_item_list:
    #     print(permission_item["permissions__url"], permission_item["permissions__title"], permission_item["permissions__menu_id"])
    permission_url_list = []  # 用户权限url列表，--> 用于中间件验证用户权限
    permission_menu_list = []  # 用户权限url所属菜单列表 [{"title":xxx, "url":xxx, "menu_id": xxx},{},]

    for item in permission_item_list:
        if "/manufacturing/assemble/" in item["permissions__url"]:
            if not step_name_list:
                del item
                continue
            elif item["permissions__title"] not in step_name_list:
                del item
                continue
        permission_url_list.append(item['permissions__url'])
        if item['permissions__menu_id']:
            temp = {"title": item['permissions__title'],
                    "url": item["permissions__url"],
                    "menu_id": item["permissions__menu_id"]}
            permission_menu_list.append(temp)

    menu_list = list(Menu.objects.values('id', 'title', 'parent_id', 'icon'))
    # print(menu_list)
    # 注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session， 加list()转为可序列化对象
    # for menu in menu_list:
    #     print(menu)
    # for p_menu in permission_menu_list:
    #     print(p_menu)
    from django.conf import settings

    request.session[settings.SESSION_PERMISSION_URL_KEY] = permission_url_list

    # 保存 权限菜单 和所有 菜单
    request.session[settings.SESSION_MENU_KEY] = {
        settings.ALL_MENU_KEY: menu_list,
        settings.PERMISSION_MENU_KEY: permission_menu_list,
    }


def refresh_permission(request):
    del request.session[settings.SESSION_PERMISSION_URL_KEY]
    del request.session[settings.SESSION_MENU_KEY][settings.ALL_MENU_KEY]
    del request.session[settings.SESSION_MENU_KEY][settings.PERMISSION_MENU_KEY]
    del request.session[settings.SESSION_MENU_KEY]
    # print("refresh_permission")
    # init_permission(request, request.user)
    return request





