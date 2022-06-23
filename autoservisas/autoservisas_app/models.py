from django.db import models
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.models import User
from datetime import date
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _


class CarModel(models.Model):
    make = models.CharField(
        _("Make"),
        max_length=200,
        help_text=_("Enter make (e.g. Daewoo)"),
    )
    model = models.CharField(
        _("Model"),
        max_length=200,
        help_text=_("Enter model (e.g. Matiz)"),
    )
    car_photo = models.ImageField(_("Car photo"), upload_to="car_photos", null=True)

    def __str__(self):
        return f"{self.make} {self.model}"

    def display_car(self):
        return ", ".join(str(car.license_plate) for car in self.cars.all()[:3])

    display_car.short_description = _("Car")

    class Meta:
        db_table = "Automobilio_modelis"
        verbose_name = _("Model")
        verbose_name_plural = _("Models")


class Car(models.Model):

    car_model = models.ForeignKey(
        CarModel, on_delete=models.RESTRICT, related_name="cars"
    )
    license_plate = models.CharField(
        _("Plate_number"),
        max_length=200,
        help_text=_("Enter plate number"),
    )
    vin_number = models.CharField(
        _("VIN"),
        max_length=200,
        help_text=_("Enter car's plate number"),
    )
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    description = HTMLField(default="")

    def __str__(self):
        return f"{self.client} {self.license_plate}"

    def display_order(self):
        return ", ".join(str(order.id) for order in self.orders.all())

    display_order.short_description = _("Order")

    class Meta:
        db_table = "Automobilis"


class Service(models.Model):
    price = models.FloatField(_("Price"), help_text=_("Enter service price"))
    name = models.CharField(
        _("Service title"),
        max_length=200,
        help_text=_("Enter service title (e.g. Change wheels)"),
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

    def in_progress_or_done(self):
        return self.filter(models.Q(status__exact="5") | models.Q(status__exact="3"))

    # def taken_books_read_by_me_ordered_by_due_back(self, user):
    #     return self.done().my_orders(user).order_by_due_back()


class Order(models.Model):
    objects = OrderQuerySet.as_manager()
    car_owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    car = models.ForeignKey(Car, on_delete=models.RESTRICT, related_name="orders")
    date = models.DateField(
        _("Date"), help_text=_("Date of received order"), auto_now_add=True
    )
    amount = models.FloatField(
        _("Amount"), help_text=_("Leave empty"), null=True, blank=True
    )
    service = models.ManyToManyField(Service, through="OrderRow")
    due_back = models.DateField(_("Due_back"), null=True, blank=True)

    ORDER_STATUS = (
        ("1", _("Received")),
        ("2", _("Accepted")),
        ("3", _("In progress")),
        ("4", _("Overdue")),
        ("5", _("Done")),
    )

    status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS,
        blank=True,
        default="1",
        help_text=_("Status"),
    )

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("order-detail", args=[str(self.id)])

    def display_service(self):
        return ", ".join(service.name for service in self.service.all())

    display_service.short_description = _("Service")

    def total_sum(self):
        orders_amount = self.order_rows.aggregate(Sum("price"))
        return orders_amount["price__sum"]

    # def update_order_amount(self):
    #     self.amount = self.total_sum()
    #     return self.amount

    def save(self, *args, **kwargs):
        self.amount = self.total_sum()
        super().save(*args, **kwargs)

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
        Order, on_delete=models.CASCADE, related_name="order_rows"
    )
    quantity = models.IntegerField(
        _("Quantity"), help_text=_("Enter quantity"), default=0
    )
    price = models.FloatField(_("Price"), help_text=_("Leave empty"), default=0)

    def __str__(self):
        return f"{self.quantity} {self.price}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("orderrow-detail", args=[str(self.id)])

    @property
    def update_order_price(self):
        self.price = self.quantity * self.service.price
        return self.price

    def save(self, *args, **kwargs):
        self.price = self.update_order_price
        super().save(*args, **kwargs)
        self.order.save()

    class Meta:
        db_table = "Uzsakymo_eilute"


class OrderReview(models.Model):
    order = models.ForeignKey("Order", on_delete=models.RESTRICT, null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField(_("Review"), max_length=2000)
