from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Transfer
from .forms import TransferForm

def transfer_stock(request):
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = Transfer.objects.create(
                variant = form.cleaned_data["variant"],
                source = form.cleaned_data["source"],
                destination = form.cleaned_data["destination"],
                quantity = form.cleaned_data["quantity"],)
            
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