from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def report_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            redirect_url = request.POST.get("next", "/reports/expensiveproducts")
            login(request, user)
            return redirect(redirect_url)
        else:
            error_message = "Invalid username or password"
            return render(
                request, "report_login.html", {"error_message": error_message}
            )
    return render(request, "report_login.html")
