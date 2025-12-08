from rest_framework import  status
from orders.serializers import OrderSerializer
from orders.models import Order
from rest_framework.response import Response
from rest_framework.decorators import api_view 
from django.contrib.auth.models import User
from django.db import transaction

@transaction.atomic
@api_view(['POST'])
def upload_orders(request):
    data = request.data

    try:
        user = User.objects.get(username=data['user'])
    except User.DoesNotExist:
        return Response({"error": f"User {data['user']} not found"},
                        status=status.HTTP_400_BAD_REQUEST)

    results = []
    errors = []

    for order_data in data["orders"]:
        order_data.pop("created_at", None)
        order_data["user"] = user.id

        serializer = OrderSerializer(data=order_data)

        if serializer.is_valid():
            order = serializer.save()   # create() сам решит create/update
            results.append(OrderSerializer(order).data)
        else:
            errors.append({
                "order_number": order_data.get("order_number"),
                "errors": serializer.errors
            })

    if errors:
        return Response(
            {"updated": results, "errors": errors},
            status=status.HTTP_207_MULTI_STATUS
        )

    return Response(results, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['PUT'])
def update_orders(request):
    data = request.data

    try:
        user = User.objects.get(username=data['user'])
    except User.DoesNotExist:
        return Response(
             {"error": f"User {data['user']} not found"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    errors = []
    results = []

    for order_data in data['orders']:
        order_data.pop('created_at', None)

        order_data['user'] = user.id
      
        try:
            order = Order.objects.get(order_number=order_data['order_number'])
        except Order.DoesNotExist:
            errors.append({
                'order_number': order_data.get('order_number'),
                'errors': 'Order not found'
            })
            continue

        serializer = OrderSerializer(order, data=order_data, partial=True)

        if serializer.is_valid():
            print('in valid')
            order = serializer.save()
            results.append(OrderSerializer(order).data)
        else:
            errors.append({
                'order_number': order_data.get('order_number'),
                'errors': serializer.errors
            })
    
    if errors:
        return Response(
            {"updated": results, "errors": errors},
            status=status.HTTP_207_MULTI_STATUS
        )

    return Response(results, status=status.HTTP_200_OK)


 