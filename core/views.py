from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def corpus(request):
    return render(request, 'core/corpus.html')

def outils(request):
    return render(request, 'core/outils.html') 

def ressources(request):
    return render(request, 'core/ressources.html') 