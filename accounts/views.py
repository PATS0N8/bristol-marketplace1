from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import ProducerProfile

# Create your views here.


#Account settings function
@login_required
def account_settings(request):
    success = False
    if request.method == "POST":
        request.user.email = request.POST.get("email", "").strip()
        request.user.save()

        if request.user.role == "PRODUCER":
            profile, _ = ProducerProfile.objects.get_or_create(user=request.user)
            profile.business_name = request.POST.get("business_name", "").strip()
            profile.postcode = request.POST.get("postcode", "").strip()
            profile.farm_story = request.POST.get("farm_story", "").strip()
            profile.location = request.POST.get("location", "").strip()
            profile.save()

        if request.user.role == "CUSTOMER":
            from accounts.models import CustomerProfile
            profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
            profile.delivery_postcode = request.POST.get("delivery_postcode", "").strip()
            profile.save()

        success = True

    profile = None
    if request.user.role == "PRODUCER":
        profile, _ = ProducerProfile.objects.get_or_create(user=request.user)
    elif request.user.role == "CUSTOMER":
        from accounts.models import CustomerProfile
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    return render(request, "products/account_settings.html", {
        "profile": profile,
        "success": success,
    })