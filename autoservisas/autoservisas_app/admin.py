from django.contrib import admin
from .models import CarModel, Car, Service, Order, OrderRow, OrderReview


class OrderRowAdmin(admin.ModelAdmin):
    list_display = ("order", "service", "quantity", "price")
    # list_filter = ("due_back", "service")
    fieldsets = (
        ("Order details", {"fields": ("order", "price")}),
        ("Services", {"fields": ("service", "quantity")}),
    )


class OrderRowInline(admin.TabularInline):
    model = OrderRow
    readonly_fields = ("id",)
    can_delete = False
    extra = 0  # išjungia placeholder'ius


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "car",
        "display_service",
        "amount",
        "date",
        "status",
        "due_back",
        "car_owner",
    )

    fieldsets = (
        ("Car details", {"fields": ("car", "car_owner")}),
        ("Order details", {"fields": ("amount", "date", "status", "due_back")}),
    )
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


class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ("order", "date_created", "reviewer", "content")


admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderRow, OrderRowAdmin)
admin.site.register(OrderReview, OrderReviewAdmin)
