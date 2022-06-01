from django.db import models
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.models import User
from datetime import date
from tinymce.models import HTMLField


class CarModel(models.Model):
    make = models.CharField(
        "Markė",
        max_length=200,
        help_text="Įveskite markę (pvz. Daewoo)",
    )
    model = models.CharField(
        "Modelis",
        max_length=200,
        help_text="Įveskite modelį (pvz. Matiz)",
    )
    car_photo = models.ImageField(
        "Automobilio nuotrauka", upload_to="car_photos", null=True
    )

    def __str__(self):
        return f"{self.make} {self.model}"

    def display_car(self):
        return ", ".join(str(car.license_plate) for car in self.cars.all()[:3])

    display_car.short_description = "Car"

    class Meta:
        db_table = "Automobilio_modelis"
        verbose_name = "Model"
        verbose_name_plural = "Models"


class Car(models.Model):

    car_model = models.ForeignKey(
        CarModel, on_delete=models.RESTRICT, related_name="cars"
    )
    license_plate = models.CharField(
        "Valstybinis_NR",
        max_length=200,
        help_text="Įveskite valstybinius numerius",
    )
    vin_number = models.CharField(
        "VIN_kodas",
        max_length=200,
        help_text="Įveskite automobilio VIN kodą",
    )
    client = models.CharField(
        "Klientas",
        max_length=200,
        help_text="Įveskite kliento vardą",
    )
    description = HTMLField(default="")

    def __str__(self):
        return f"{self.client} {self.license_plate}"

    def display_order(self):
        return ", ".join(str(order.id) for order in self.orders.all())

    display_order.short_description = "Order"

    class Meta:
        db_table = "Automobilis"


class Service(models.Model):
    price = models.FloatField("Kaina", help_text="Įveskite užsakymo sumą")
    name = models.CharField(
        "Pavadinimas",
        max_length=200,
        help_text="Įveskite paslaugos pavadinimą (pvz. Ratų keitimas)",
    )

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("orderrow-detail", args=[str(self.id)])

    class Meta:
        db_table = "Paslauga"


class OrderQuerySet(models.QuerySet):
    # def my_orders(self, user):
    #     return self.filter(car_owner=user)

    def done(self):
        return self.filter(status__exact="5")

    def order_by_due_back(self):
        return self.order_by("due_back")

    # def taken_books_read_by_me_ordered_by_due_back(self, user):
    #     return self.done().my_orders(user).order_by_due_back()


class Order(models.Model):
    objects = OrderQuerySet.as_manager()
    car_owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    car = models.ForeignKey(Car, on_delete=models.RESTRICT, related_name="orders")
    date = models.DateField("Data", help_text="Užsakymo įvedimo data")
    amount = models.FloatField("Suma", help_text="Įveskite užsakymo sumą")
    service = models.ManyToManyField(Service, through="OrderRow")
    due_back = models.DateField("Bus grąžinta", null=True, blank=True)

    ORDER_STATUS = (
        ("1", "Gautas"),
        ("2", "Patvirtintas"),
        ("3", "Vykdomas"),
        ("4", "Vėluojamas"),
        ("5", "Atliktas"),
    )

    status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS,
        blank=True,
        default="1",
        help_text="Statusas",
    )

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("order-detail", args=[str(self.id)])

    def display_service(self):
        return ", ".join(service.name for service in self.service.all())

    display_service.short_description = "Service"

    def total_sum(self):
        orders_amount = self.order_rows.aggregate(Sum("price"))
        return orders_amount["price__sum"]

    def update_order_amount(self):
        self.amount = self.total_sum()
        self.save()
        return self.amount

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        db_table = "Uzsakymas"


class OrderRow(models.Model):

    service = models.ForeignKey(
        Service, on_delete=models.RESTRICT, related_name="service"
    )
    order = models.ForeignKey(
        Order, on_delete=models.RESTRICT, related_name="order_rows"
    )
    quantity = models.IntegerField("Kiekis", help_text="Įveskite kiekį", default=0)
    price = models.FloatField("Kaina", help_text="Įveskite kainą", default=0)

    def __str__(self):
        return f"{self.quantity} {self.price}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("orderrow-detail", args=[str(self.id)])

    def update_order_price(self):
        self.price = self.quantity * self.service.price
        self.save()

    class Meta:
        db_table = "Uzsakymo_eilute"
