from django.shortcuts import render
from django.http import HttpResponse
from .models import Car, CarModel, Service, Order
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q


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
    paginator = Paginator(CarModel.objects.all(), 2)
    page_number = request.GET.get("page")
    paged_cars = paginator.get_page(page_number)
    # cars = CarModel.objects.all()
    context = {"cars": paged_cars}
    return render(request, "cars.html", context=context)


def car(request, car_id):
    car = get_object_or_404(CarModel, pk=car_id)
    return render(request, "car.html", {"car": car})


def search(request):
    query = request.GET.get("query")
    query_filter = (
        Q(client__icontains=query)
        | Q(license_plate__icontains=query)
        | Q(vin_number__icontains=query)
        | Q(car_model__model__icontains=query)
    )
    search_results = Car.objects.filter(query_filter)
    return render(
        request, "search.html", {"cars_filter": search_results, "query": query}
    )


class OrderListView(generic.ListView):
    model = Order
    paginate_by = 2
    template_name = "order_list.html"
    context_object_name = "order_list"

    def get_queryset(self):
        return Order.objects.all()


class OrderDetailView(generic.DetailView):
    model = Order
    template_name = "order_detail.html"
