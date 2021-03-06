from django.shortcuts import render, get_object_or_404, redirect
from .models import Car, CarModel, Service, Order
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .forms import OrderReviewForm, OrderForm
from django.views.generic.edit import FormMixin
from datetime import date, timedelta


def index(request):
    num_services = Service.objects.all().count()
    completed_orders = Order.objects.filter(status__exact="5")
    num_completed_orders = completed_orders.count()
    num_cars = Car.objects.count()
    num_visits = request.session.get("num_visits", 1)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_services": num_services,
        "num_completed_orders": num_completed_orders,
        "num_cars": num_cars,
        "num_visits": num_visits,
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


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reik??mes i?? registracijos formos
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        # tikriname, ar sutampa slapta??od??iai
        if password == password2:
            # tikriname, ar neu??imtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, _("Username %s already exists!") % username)
                return redirect("register")
            else:
                # tikriname, ar n??ra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, _("Email %s already exists!") % email)
                    return redirect("register")
                else:
                    # jeigu viskas tvarkoje, sukuriame nauj?? vartotoj??
                    User.objects.create_user(
                        username=username, email=email, password=password
                    )
        else:
            messages.error(request, _("Passwords do not match!"))
            return redirect("register")
    return render(request, "register.html")


class OrderListView(generic.ListView):
    model = Order
    paginate_by = 10
    template_name = "order_list.html"
    context_object_name = "order_list"

    def get_queryset(self):
        return Order.objects.all()


class ServiceOrdersByUserListView(LoginRequiredMixin, generic.ListView):
    model = Order
    context_object_name = "orders"
    template_name = "my_orders.html"
    paginate_by = 10

    def get_queryset(self):
        # Order.objects.taken_books_read_by_me_ordered_by_due_back()
        # Order.objects.done().order_by_due_back().my_orders()
        # Order.objects.filter(car_owner=self.request.user).filter(status__exact='p').order_by('due_back')
        return (
            Order.objects.filter(car_owner=self.request.user)
            .in_progress_or_done()
            .order_by_due_back()
        )


class OrderByUserDetailView(LoginRequiredMixin, generic.DetailView):
    model = Order
    template_name = "user_order.html"


class OrderDetailView(FormMixin, generic.DetailView):
    model = Order
    template_name = "order_detail.html"
    form_class = OrderReviewForm

    class Meta:
        ordering = ["title"]

    # nurodome, kur atsidursime komentaro s??km??s atveju.
    def get_success_url(self):
        return reverse_lazy("order-detail", kwargs={"pk": self.object.id})

    # standartinis post metodo perra??ymas, naudojant FormMixin, galite kopijuoti tiesiai ?? savo projekt??.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # ??tai ??ia nurodome, kad knyga bus b??tent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijung??s.
    def form_valid(self, form):
        form.instance.order = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(OrderDetailView, self).form_valid(form)


class OrderByUserCreateView(LoginRequiredMixin, generic.CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("my-orders")
    template_name = "user_order_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["car"].queryset = Car.objects.filter(client=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.car_owner = self.request.user
        form.instance.status = "3"
        return super().form_valid(form)

    # def get_initial(self):
    #     initial = super().get_initial()
    #     order_id = self.request.GET.get('order_id')
    #     if order_id:
    #         initial['order'] = order_id
    #     initial['due_back'] = date.today() + timedelta(days=3)
    #     return initial


class OrderByUserUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("my-orders")
    template_name = "user_order_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["car"].queryset = Car.objects.filter(client=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.car_owner = self.request.user
        form.instance.status = "3"
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = True
        return context

    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial['due_back'] = date.today() + timedelta(days=7)
    #     return initial

    def test_func(self):
        return (
            self.request.user == self.get_object().car_owner
            and self.get_object().status != "5"
        )


class OrderByUserDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):
    model = Order
    success_url = reverse_lazy("my-orders")
    template_name = "user_order_delete.html"

    def form_valid(self, form):
        messages.success(self.request, f'{_("Order deleted").capitalize()}')
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().car_owner
