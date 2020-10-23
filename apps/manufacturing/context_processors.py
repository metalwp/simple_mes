from apps.process_manager.models import ProcessStep
from apps.order_manager.models import Order


def test(request):
    try:
        order = Order.objects.filter_without_isdelete().get(status=1)
    except (Order.DoesNotExist, Order.MultipleObjectsReturned):
        return {'manufacturing_steps': []}
    route = order.product_model.process_route
    steps = ProcessStep.objects.filter_without_isdelete().filter(fixture=None, process_route=route).\
        order_by('sequence_no')
    return {'manufacturing_steps': steps}

