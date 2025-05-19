from django.shortcuts import render, redirect, get_object_or_404
from .models import Question
from .forms import QuestionForm, AnswerForm
from django.db.models import Q
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.services import NotificationService

def ask_question(request):
    query = request.GET.get('q')
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            existing = Question.objects.filter(title__icontains=title)
            if existing.exists():
                return render(request, 'QA/duplicate_found.html', {'questions': existing})
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return redirect('QA:question_detail', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'QA/ask_question.html', {'form': form})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all()
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            # NOTIFICATION à l'auteur de la question
            if question.author != request.user:
                NotificationService.create_notification(
                    recipient=question.author,
                    notification_type='QA_ANSWER',
                    title="Nouvelle réponse à votre question",
                    message=f"{request.user.username} a répondu à votre question « {question.title} ».",
                    related_object=question,
                    action_url=question.get_absolute_url()
                )
            return redirect('QA:question_detail', pk=pk)
    else:
        form = AnswerForm()
    return render(request, 'QA/question_detail.html', {'question': question, 'answers': answers, 'form': form})

def search_questions(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Question.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'QA/search.html', {'results': results, 'query': query})


def qa_home(request):
    query = request.GET.get('q')
    if query:
        questions = Question.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        questions = Question.objects.order_by('-created_at')
    return render(request, 'QA/qa_list.html', {'questions': questions, 'query': query})
