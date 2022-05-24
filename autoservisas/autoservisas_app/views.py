from django.shortcuts import render
from django.http import HttpResponse
from .models import Car, CarModel, Service, Order
from django.shortcuts import render, get_object_or_404
from django.views import generic

def index(request):
    num_services = Service.objects.all().count()

    completed_orders = Order.objects.filter(status__exact="5")
    num_completed_orders = completed_orders.count()

    num_cars = Car.objects.count()

    context = {
        "num_services": num_services,
        "num_completed_orders": num_completed_orders,
        "num_cars": num_cars,
    }

    return render(request, "index.html", context=context)

def cars(request):
    
    cars = CarModel.objects.all()
    context = {
        'cars': cars
    }
    return render(request, 'cars.html', context=context)

def car(request, car_id):
    car = get_object_or_404(CarModel, pk=car_id)
    return render(request, 'car.html', {'car': car})

class OrderListView(generic.ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'order_list'

    def get_queryset(self):
        return Order.objects.all() 

class OrderDetailView(generic.DetailView):
    model = Order
    template_name = 'order_detail.html'