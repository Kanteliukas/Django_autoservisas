from django.shortcuts import render
from django.http import HttpResponse
from .models import Car, Service, Order


def index(request):

    # Suskaičiuokime keletą pagrindinių objektų
    num_services = Service.objects.all().count()
    # num_instances = BookInstance.objects.all().count()

    # # Laisvos knygos (tos, kurios turi statusą 'g')
    completed_orders = Order.objects.filter(status__exact="5")
    num_completed_orders = completed_orders.count()

    # # Kiek yra automobilių
    num_cars = Car.objects.count()

    # # perduodame informaciją į šabloną žodyno pavidale:
    context = {
        "num_services": num_services,
        "num_completed_orders": num_completed_orders,
        "num_cars": num_cars,
    }

    # # renderiname index.html, su duomenimis kintamąjame context
    return render(request, "index.html", context=context)
