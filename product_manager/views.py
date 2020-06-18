from django.shortcuts import render, redirect

from .models import ProductModel, ProductCategory

# Create your views here.


def pc_index(request):
    product_category = ProductCategory.objects.all()
    return render(request, 'product_manager/pc_index.html', locals())


def pc_create(request):
    if request.method == "GET":
        product_category_now = ProductCategory.objects.all()
        return render(request, 'product_manager/pc_create.html', locals())
    elif request.method == "POST":
        if request.POST.get('submit_btn') == '保存':
            _category_name = request.POST.get('category_name')
            _parent_category = request.POST.get('parent_category')
            if _parent_category != _category_name:
                if _parent_category:
                    _parent_cate = ProductCategory.objects.get(category_name=_parent_category)
                    pc, created = ProductCategory.objects.update_or_create(category_name=_category_name, defaults={'parent_category':_parent_cate})
                else:
                    pc, created = ProductCategory.objects.update_or_create(category_name=_category_name, defaults={'parent_category':None})
            else:
                return
            return redirect('/product_category/pc_index/')
        else:
            return redirect('/product_category/pc_index/')


def pm_index(request):
    product_model = ProductModel.objects.all()
    return render(request, 'product_manager/pm_index.html', locals())