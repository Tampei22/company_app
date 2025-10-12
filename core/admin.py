from django.contrib import admin
from .models import AgentiComerciali, Contracte, Factura, Plata, ContBancar

@admin.register(AgentiComerciali)
class AgentiComercialiAdmin(admin.ModelAdmin):
    list_display = (
        "cod", "denumirea", "cod_fiscal", "denumirea_completa",
        "conducator", "forma_juridica", "adresa_juridica",
        "adresa_postala", "telefoane", "email"
    )
    search_fields = ("denumirea", "cod_fiscal", "cod")


@admin.register(Contracte)
class ContracteAdmin(admin.ModelAdmin):
    list_display = (
        "cod", "denumirea", "nr_contractului",
        "data_contractului", "termen_valabilitate",
        "suma_contractului", "cota_avans", "suma_in_valuta",
        "suma_ramasa", "agent"
    )
    list_filter = ("data_contractului", "termen_valabilitate", "agent")
    search_fields = ("cod", "denumirea", "nr_contractului")

    readonly_fields = ("suma_ramasa",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        "id", "numar", "data_facturii",
        "suma_facturii", "valuta", "contract"
    )
    list_filter = ("data_facturii", "valuta")
    search_fields = ("numar", "contract__denumirea")


@admin.register(Plata)
class PlataAdmin(admin.ModelAdmin):
    list_display = (
        "id", "factura", "data_platii",
        "suma_platita", "metoda", "numar_document"
    )
    list_filter = ("metoda", "data_platii")
    search_fields = ("numar_document", "factura__numar")

@admin.register(ContBancar)
class ContBancarAdmin(admin.ModelAdmin):
    list_display = ("denumirea", "iban", "tip_cont", "valuta", "data_deschiderii", "data_inchiderii")
    search_fields = ("denumirea", "iban")