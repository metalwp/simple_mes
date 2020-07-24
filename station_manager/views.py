from django.shortcuts import render
from django.views.generic import ListView, DetailView

from station_manager.models import Station

# Create your views here.


class IndexView(ListView):
    """视图类"""
    model = Station
    template_name = "station_manager/index.html"
    context_object_name = 'station'

    def get_queryset(self):
        print(self.request.GET.dict())
        # cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        # return super(CategoryView, self).get_queryset().filter(category=cate)
        pass