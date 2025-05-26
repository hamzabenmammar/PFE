from django.http import JsonResponse
from django.shortcuts import render
import requests

def chatbot_interface(request):
    return render(request, "chatbot/chatbot.html")  # ton template

def ask_bot(request):
    question = request.GET.get("question")
    if not question:
        return JsonResponse({"error": "question vide"}, status=400)

    try:
        # Appelle ton API FastAPI qui tourne sur le port 8000
        res = requests.post("http://127.0.0.1:8000/query", json={"question": question})
        res.raise_for_status()
        return JsonResponse(res.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
