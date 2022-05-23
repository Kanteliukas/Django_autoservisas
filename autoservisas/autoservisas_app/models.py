from django.db import models
from django.urls import reverse


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

    def __str__(self):
        return f"{self.make} {self.model}"

    class Meta:
        db_table = "Automobilio_modelis"
        verbose_name = 'Model'
        verbose_name_plural = 'Models'


class Car(models.Model):
    
    car_model = models.ForeignKey(CarModel, on_delete=models.RESTRICT, related_name='cars')
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

    def __str__(self):
        return f"{self.client} {self.license_plate}"

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


class Order(models.Model):

    car = models.ForeignKey(Car, on_delete=models.RESTRICT, related_name='orders')
    date = models.DateField("Data", help_text="Užsakymo įvedimo data")    
    amount = models.FloatField("Suma", help_text="Įveskite užsakymo sumą")
    service = models.ManyToManyField(Service, through="OrderRow")

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("order-detail", args=[str(self.id)])
    
    def display_service(self):
            return ', '.join(service.name for service in self.service.all()[:3])

    display_service.short_description = 'Service'

    class Meta:
        db_table = "Uzsakymas"


class OrderRow(models.Model):
    
    service = models.ForeignKey(Service, on_delete=models.RESTRICT)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    date = models.DateField("Data", help_text="Užsakymo įvedimo data")
    amount = models.FloatField("Suma", help_text="Įveskite užsakymo sumą")

    def __str__(self):
        return f"{self.date} {self.amount}"

    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse("orderrow-detail", args=[str(self.id)])

    class Meta:
        db_table = "Uzsakymo_eilute"
