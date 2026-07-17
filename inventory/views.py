from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Transfer
from .forms import TransferForm

def transfer_stock(request):
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            variant = form.cleaned_data["variant"]
            quantity = form.cleaned_data["quantity"]
            unit = form.cleaned_data["unit"]
            if unit == "cartons":
                if variant.pieces_per_carton is None:
                    messages.error(request, "This variant is counted in pieces only — it has no carton size.")
                    return render(request, "inventory/transfer.html", {"form": form})
                quantity = quantity * variant.pieces_per_carton

 
            transfer = Transfer.objects.create(
                variant = variant,
                source = form.cleaned_data["source"],
                destination = form.cleaned_data["destination"],
                quantity = quantity,)
            
            try:
                transfer.execute()
                messages.success(request, "Transfer completed successfully")
                return redirect("transfer_stock")
            except ValidationError as e:
                transfer.delete()
                messages.error(request, e.message)


    else:
        form = TransferForm()


    return render(request, "inventory/transfer.html", {"form":form})