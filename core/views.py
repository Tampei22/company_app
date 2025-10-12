from django.shortcuts import render, get_object_or_404, redirect
from .models import AgentiComerciali, Contracte, Factura, Plata, ContBancar
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from datetime import datetime
from django.db.models import Q
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .forms import ContBancarForm
from django.contrib import messages
from django.http import JsonResponse

@login_required
def home(request):
    return render(request, "core/base.html")

# agenti
class SupplierForm(forms.ModelForm):
    class Meta:
        model = AgentiComerciali
        fields = [
            "cod", "denumirea", "cod_fiscal", "denumirea_completa",
            "conducator", "forma_juridica", "adresa_juridica", "adresa_postala",
            "telefoane", "email", "rezident", "tara", "cod_tva",
            "cont_bancar_iban", "contract_baza"
        ]
       
@login_required
def supplier_list(request):
    suppliers = AgentiComerciali.objects.all()
    return render(request, "core/supplier_list.html", {"suppliers": suppliers})

def supplier_add(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()
    return render(request, "core/supplier_form.html", {"form": form})

def supplier_edit(request, pk):
    supplier = get_object_or_404(AgentiComerciali, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "core/supplier_form.html", {"form": form})

def supplier_delete(request, pk):
    supplier = get_object_or_404(AgentiComerciali, pk=pk)
    supplier.delete()
    return redirect("supplier_list")

# контракты

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contracte
        fields = [
            "cod", "denumirea", "institutia", "programul", "componente_de_sursa",
            "originea_sursei", "iban", "eco", "agent", "contul_de_decontare",
            "nr_contractului", "data_contractului", "conditii_plata",
            "termen_valabilitate", "suma_contractului", "cota_avans",
            "suma_in_valuta", "cod_obiectului", "cod_valutei",
            "continut_prescurtat", "data_indeplinirii_obligatiilor",
            "masura", "contractul_nu_este_inregistrat_la_trezorerie",
            "prin_achizitii_publice", "contract_produse_alimentare"
        ]
        widgets = {
            "data_contractului": forms.DateInput(attrs={"type": "date"}),
            "termen_valabilitate": forms.DateInput(attrs={"type": "date"}),
            "data_indeplinirii_obligatiilor": forms.DateInput(attrs={"type": "date"}),
        }

@login_required(login_url='login')
def contract_list(request):
    contracts = Contracte.objects.select_related("agent").all()

    return render(
        request,
        "core/contract_list.html",
        {"contracts": contracts},
    )

def contract_add(request):
    if request.method == "POST":
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contract_list")
    else:
        form = ContractForm()
    return render(request, "core/contract_form.html", {"form": form})


def contract_edit(request, pk):
    contract = get_object_or_404(Contracte, pk=pk)
    if request.method == "POST":
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return redirect("contract_list")
    else:
        form = ContractForm(instance=contract)
    return render(request, "core/contract_form.html", {"form": form})


def contract_delete(request, pk):
    contract = get_object_or_404(Contracte, pk=pk)
    contract.delete()
    return redirect("contract_list")

#накладные

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ["contract", "numar", "data_facturii", "suma_facturii", "valuta", "comentariu"]
        widgets = {
            "data_facturii": forms.DateInput(attrs={"type": "date"}),
        }

@login_required(login_url='login')
def factura_list(request):
    contract_id = request.GET.get("contract")
    facturi = Factura.objects.select_related("contract").all()

    if contract_id:
        facturi = facturi.filter(contract_id=contract_id)

    total_sum = facturi.aggregate(total=Sum("suma_facturii"))["total"] or 0
    print("DEBUG total_sum =", total_sum)

    return render(
        request,
        "core/factura_list.html",
        {"facturi": facturi, "total_sum": total_sum},
    )

def factura_add(request):
    if request.method == "POST":
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save(commit=False)
            contract = factura.contract

            total_facturi = (
                Factura.objects.filter(contract=contract)
                .aggregate(Sum("suma_facturii"))["suma_facturii__sum"] or 0
            )
            suma_contractului = contract.suma_contractului or 0
            noua_suma = factura.suma_facturii or 0
            
            if total_facturi + noua_suma > suma_contractului:
                context = {
                    "form": form,
                    "error_modal": (
                        f"Suma totală a facturilor ({total_facturi + noua_suma:.2f} MDL) "
                        f"depășește suma contractului ({suma_contractului:.2f} MDL)."
                    ),
                }
                return render(request, "core/factura_form.html", context)

            factura.save()
            messages.success(request, "Factura a fost adăugată cu succes.")
            return redirect("factura_list")
        else:
            return render(request, "core/factura_form.html", {"form": form})
    else:
        form = FacturaForm()

    return render(request, "core/factura_form.html", {"form": form})

def factura_edit(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == "POST":
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            return redirect("factura_list")
    else:
        form = FacturaForm(instance=factura)
    return render(request, "core/factura_form.html", {"form": form})


def factura_delete(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    factura.delete()
    return redirect("factura_list")

class PlataForm(forms.ModelForm):
    class Meta:
        model = Plata
        fields = ["factura", "data_platii", "suma_platita", "metoda", "numar_document"]
        widgets = {
            "data_platii": forms.DateInput(attrs={"type": "date"}),
        }

class PlataForm(forms.ModelForm):
    class Meta:
        model = Plata
        fields = ["factura", "data_platii", "suma_platita", "metoda", "numar_document"]

@login_required(login_url='login')
def plata_list(request):
    plati = Plata.objects.select_related("factura").all()
    return render(request, "core/plata_list.html", {"plati": plati})



def plata_add(request):
    if request.method == "POST":
        form = PlataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("plata_list")
    else:
        form = PlataForm()
    return render(request, "core/plata_form.html", {"form": form})



def plata_edit(request, pk):
    plata = get_object_or_404(Plata, pk=pk)
    if request.method == "POST":
        form = PlataForm(request.POST, instance=plata)
        if form.is_valid():
            form.save()
            return redirect("plata_list")
    else:
        form = PlataForm(instance=plata)
    return render(request, "core/plata_form.html", {"form": form})


def plata_delete(request, pk):
    plata = get_object_or_404(Plata, pk=pk)
    plata.delete()
    return redirect("plata_list")


def plata_detail(request, pk):
    plata = get_object_or_404(Plata, pk=pk)
    return render(request, "core/plata_detail.html", {"plata": plata})
print("DEBUG: plata_detail загружена")



def report_plati(request):
    plati = Plata.objects.select_related("factura__contract").all()
    return render(request, "core/report_plati.html", {"plati": plati})


def plata_pdf(request, pk):
    plata = get_object_or_404(Plata, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="plata_{plata.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Платежка")
    y -= 40

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"ID: {plata.id}"); y -= 20
    p.drawString(50, y, f"Дата: {plata.data_platii}"); y -= 20
    p.drawString(50, y, f"Сумма: {plata.suma_platita}"); y -= 20
    p.drawString(50, y, f"Метод оплаты: {plata.metoda}"); y -= 20
    p.drawString(50, y, f"Документ: {plata.numar_document}"); y -= 20
    p.drawString(50, y, f"Накладная: {plata.factura.numar}"); y -= 20
    p.drawString(50, y, f"Контракт: {plata.factura.contract.denumirea}"); y -= 20

    p.showPage()
    p.save()
    return response


def report_contracts(request):
    contracts = Contracte.objects.select_related("agent").all()
    return render(request, "core/report_contracts.html", {"contracts": contracts})


def factura_archive(request):
    facturi = Factura.objects.select_related("contract").all()
    data = request.GET.get("data")
    otpravitel = request.GET.get("otpravitel")
    poluchatel = request.GET.get("poluchatel")
    numar = request.GET.get("numar")

    if data:
        if data.startswith(">"):
            try:
                d = datetime.strptime(data[1:], "%Y-%m-%d").date()
                facturi = facturi.filter(data_facturii__gte=d)
            except:
                pass
        else:
            facturi = facturi.filter(data_facturii=data)

    if otpravitel:
        facturi = facturi.filter(contract__institutia__icontains=otpravitel)

    if poluchatel:
        facturi = facturi.filter(contract__denumirea__icontains=poluchatel)

    if numar:
        facturi = facturi.filter(numar__icontains=numar)

    return render(request, "core/factura_archive.html", {"facturi": facturi})

class ContBancarForm(forms.ModelForm):
    class Meta:
        model = ContBancar
        fields = [
            "denumirea", "iban", "tip_cont", "prin_trezoreria", "decontari_directe",
            "valuta", "denumirea_trezoreriei", "cod_fiscal_trezorerie", "numar_cont_trezorerie",
            "banca_organizatiei", "banca_corespondent", "data_deschiderii", "data_inchiderii"
        ]
        widgets = {
            "data_deschiderii": forms.DateInput(attrs={"type": "date"}),
            "data_inchiderii": forms.DateInput(attrs={"type": "date"}),
        }

def cont_bancar_list(request, supplier_id):
    supplier = get_object_or_404(AgentiComerciali, pk=supplier_id)
    conturi = ContBancar.objects.filter(agent=supplier)
    return render(request, 'core/cont_bancar_list.html', {'supplier': supplier, 'conturi': conturi})

def cont_bancar_add(request, supplier_id):
    supplier = get_object_or_404(AgentiComerciali, pk=supplier_id)

    if request.method == 'POST':
        form = ContBancarForm(request.POST)
        if form.is_valid():
            cont = form.save(commit=False)
            cont.agent = supplier
            cont.save()
            return redirect('cont_bancar_list', supplier_id=supplier.pk)
    else:
        form = ContBancarForm()

    return render(request, 'core/cont_bancar_form.html', {
        'form': form,
        'supplier': supplier
    })

def cont_bancar_edit(request, supplier_id, pk):
    supplier = get_object_or_404(AgentiComerciali, pk=supplier_id)
    cont = get_object_or_404(ContBancar, pk=pk, agent=supplier)

    if request.method == 'POST':
        form = ContBancarForm(request.POST, instance=cont) 
        if form.is_valid():
            form.save()                                 
            return redirect('cont_bancar_list', supplier_id=supplier.pk)
    else:
        form = ContBancarForm(instance=cont)

    return render(request, 'core/cont_bancar_form.html', {'form': form, 'supplier': supplier})


def cont_bancar_delete(request, pk):
    cont = get_object_or_404(ContBancar, pk=pk)
    agent_id = cont.agent.id
    cont.delete()
    return redirect("supplier_edit", pk=agent_id)
