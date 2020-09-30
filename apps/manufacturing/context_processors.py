from apps.process_manager.models import ProcessStep
from apps.order_manager.models import Order


def test(request):
    try:
        order = Order.objects.get(status=1)
    except (Order.DoesNotExist, Order.MultipleObjectsReturned):
        return {'steps': []}
    route = order.product_model.process_route
    steps = ProcessStep.objects.filter_without_isdelete().filter(fixture=None, process_route=route).\
        order_by('sequence_no')
    return {'steps': steps}

