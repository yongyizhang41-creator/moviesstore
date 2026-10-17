from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
from cart.models import Item

@staff_member_required(login_url="accounts.login")
def top_purchaser(request):
    top_user = (
        User.objects
        .annotate(movies_purchased=Sum("order__item__quantity"))
        .filter(movies_purchased__gt=0)
        .order_by("-movies_purchased", "username")
        .first()
    )

    purchases = []
    if top_user:
        purchases = (
            Item.objects
            .filter(order__user=top_user)
            .values("movie_id", "movie__name")
            .annotate(purchase_count=Sum("quantity"))
            .order_by("-purchase_count","movie__name")
        )

    template_data = {}
    template_data["title"] = "Top Purchaser"
    template_data["top_user"] = top_user
    template_data["purchases"] = purchases

    return render(request, "dashboard/top_purchaser.html", {"template_data": template_data})