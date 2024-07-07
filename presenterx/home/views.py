from django.shortcuts import render, HttpResponse

# Create your views here.
def index(request):
    return render(request, "index.html")
    # return HttpResponse("This is Homepage")

def about(request):
    return render(request, "about.html")
    #return HttpResponse("This is About Page")

def features(request):
    return render(request, "features.html")
    #return HttpResponse("This is controls Page")

def contact(request):
    return render(request, "contact.html")
    #return HttpResponse("This is Contact Page")