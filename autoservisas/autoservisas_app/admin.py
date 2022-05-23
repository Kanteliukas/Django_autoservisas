from django.contrib import admin
from .models import CarModel, Car, Service, Order, OrderRow


class OrderRowAdmin(admin.ModelAdmin):
    list_display = ("order", "service", "amount", "date")
    list_filter = ("date", "service")
    fieldsets = (
        ("General", {"fields": ("order", "date")}),
        ("Services", {"fields": ("service", "amount")}),
    )


class OrderRowInline(admin.TabularInline):
    model = OrderRow
    readonly_fields = ("id",)
    can_delete = False
    extra = 0  # išjungia placeholder'ius


class OrderAdmin(admin.ModelAdmin):
    list_display = ("car", "display_service", "amount", "date", "status")
    inlines = [OrderRowInline]


class CarModelAdmin(admin.ModelAdmin):
    list_display = ("make", "model", "display_car")


class CarAdmin(admin.ModelAdmin):
    list_display = (
        "car_model",
        "display_order",
        "license_plate",
        "vin_number",
        "client",
    )
    list_filter = ("client", "car_model")
    search_fields = ("license_plate", "vin_number")


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    list_filter = ("name", "price")


admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderRow, OrderRowAdmin)
