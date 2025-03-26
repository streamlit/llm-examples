from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from api import models
from django.views.decorators.csrf import csrf_exempt 
import openai
import os
from .utils import get_short_term_memory, save_short_term_memory
from django.http import JsonResponse

import json
import markdown
from django.utils.safestring import mark_safe

# Create your views here.
@login_required
@staff_member_required
def view_users(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('users_page')
    else:
        form = CustomUserForm()
    
    users = User.objects.all() 
    return render(request, 'users_page.html', {'form': form, 'users': users})

@login_required
@staff_member_required
def view_training_files(request):
    return render(request, 'trainingFiles.html')

@login_required
def view_profile(request):
    return render(request, 'profile.html')


@login_required
@staff_member_required
def training_list(request):
    if request.method == 'POST':
        form = LuluTrainningForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('training_list') 
    else:
        form = LuluTrainningForm()

    trainings = models.luluTrainning.objects.all()
    return render(request, 'trainingFiles.html', {'form': form, 'trainings': trainings})

@login_required
def view_home(request):
    return render(request, 'home.html')

@login_required
def view_profile(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile') 
    else:
        form = EditUserForm(instance=request.user)
    
    return render(request, 'profile.html', {'form': form})

@login_required
@csrf_exempt
def view_lulu(request):
    if request.method == 'GET':
        return render(request, 'lulu.html')
    
    elif request.method == 'POST':
        question = request.POST.get('question')
        user_id = request.user.id 
        
        recent_memory = get_short_term_memory(user_id)

        messages = [
            {"role": "system", "content": "Lulu is a friendly, empathetic assistant designed to help students improve their language skills in Luxembourgish, German, and French."},
            {"role": "user", "content": "What's your name?"},
            {"role": "assistant", "content": "Hey there! I'm Lulu, your language-learning buddy! How can I help you today?", "weight": 1},
            {"role": "system", "content": "Your name is Lulu, you're a friend who will help children and teenagers on their academic journeys, aiming to show the positivity of life with sweetness and sensitivity."}
        ]

        for msg in recent_memory:
            messages.append({"role": "user", "content": msg})

        messages.append({"role": "user", "content": question})

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        def stream_gpt():
            result = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )

            response_text = ""
            for chunk in result:
                if chunk.choices and chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content

            response_text_html = markdown.markdown(text=response_text,output_format='html')

            # Salvar a conversa no banco de dados após a resposta completa
            models.chat_memories.objects.create(
                user_id=request.user.id,
                user_message=question,
                chat_message=response_text
            )

            yield response_text_html 

        save_short_term_memory(user_id, question)

        response_server = StreamingHttpResponse(stream_gpt(), content_type="text/html; charset=utf-8")
        response_server['Cache-Control'] = 'no-cache'
        response_server['X-Accel-Buffering'] = 'no'
        
        return response_server
    
@login_required
def view_chat_memory(request):
    if request.user.is_authenticated:
        conversas = models.chat_memories.objects.filter(user_id=str(request.user.id))
    else:
        conversas = models.chat_memories.objects.none()

    return render(request, 'chat_memory.html', {'conversas': conversas})

@login_required
def view_diary(request):
    entries = models.diary_facts.objects.filter(user=request.user).order_by('-date')  
    return render(request, 'diary.html', {'entries': entries})

def create_diary(request):
    if request.method == 'POST':
        form = diaryForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user  # Associa o usuário autenticado
            form.save()  # Salva o diário
            return redirect('diary')  # Redireciona para a página de visualização do diário
    else:
        form = diaryForm()

    return render(request, 'diary.html', {'form': form})

def diary_view(request):
    entries = models.diary_facts.objects.filter(user=request.user).order_by('-date')  
    return render(request, 'diary.html', {'entries': entries})

@login_required
@staff_member_required
def view_chat_management_onboarding_questions(request):
     
    if request.method == 'POST':
        form = questionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('adm_onboarding_questions')
    else:
        form = questionForm()
    
    questions = models.chat_dim_onboarding_questions.objects.all().order_by('order')
    return render(request,'adm_onboarding.html',{'questions': questions, 'form':form})

@login_required
@staff_member_required
def update_question_active(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            active = data.get('active')
            question = models.chat_dim_onboarding_questions.objects.get(id=id)
            question.active = active
            question.save()
            return JsonResponse({'success': True})
        except models.chat_dim_onboarding_questions.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def view_chat_dim_onboarding_questions(request):
    questions = models.chat_dim_onboarding_questions.objects.all().prefetch_related("options")
    return render(request, "adm_onboarding.html", {"questions": questions})

@login_required
@staff_member_required
@csrf_exempt
def add_option(request):
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = data.get("question_id")
        option_text = data.get("option")

        question = models.chat_dim_onboarding_questions.objects.get(id=question_id)
        new_option = models.chat_dim_onboarding_options_answers.objects.create(question=question, option=option_text)
        new_option.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@csrf_exempt
def delete_option(request, option_id):
    if request.method == "DELETE":
        try:
            option = models.chat_dim_onboarding_options_answers.objects.get(id=option_id)
            option.delete()
            return JsonResponse({"success": True})
        except models.chat_dim_onboarding_options_answers.DoesNotExist:
            return JsonResponse({"success": False}, status=404)

    return JsonResponse({"success": False}, status=400)


########### Onboarding
@login_required
def onboarding_data(request):
    """Retorna as perguntas de onboarding não respondidas em JSON com opções associadas."""
    
    # Obter o usuário atual
    user = request.user

    # Obter todas as perguntas ativas do onboarding
    questions = models.chat_dim_onboarding_questions.objects.filter(active=True).order_by("order")

    # Obter as perguntas já respondidas pelo usuário
    answered_questions = models.chat_facts_onboarding_answers.objects.filter(user=user).values_list('question_id', flat=True)

    # Filtrar as perguntas não respondidas
    unanswered_questions = questions.exclude(id__in=answered_questions)

    # Obter todas as opções de resposta
    options = models.chat_dim_onboarding_options_answers.objects.all()

    # Agrupar as opções por pergunta
    grouped_options = {}
    for option in options:
        if option.question.id not in grouped_options:
            grouped_options[option.question.id] = []
        grouped_options[option.question.id].append(option.option)

    # Preparando o JSON de resposta com as perguntas não respondidas e suas respectivas opções
    data = {
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "options": grouped_options.get(question.id, [])
            }
            for question in unanswered_questions
        ]
    }

    return JsonResponse(data)



@login_required
@csrf_exempt 
def save_onboarding_answer(request):
    if request.method == 'POST':
        try:
            # Capturar os dados enviados via POST
            data = json.loads(request.body)
            question_id = data.get('question_id')
            answer = data.get('answer')

            # Verificar se os dados estão completos
            if not question_id or answer is None:
                return JsonResponse({'status': 'error', 'message': 'Dados incompletos'}, status=400)

            # Obter a pergunta correspondente pelo ID
            question = models.chat_dim_onboarding_questions.objects.get(id=question_id)

            # Obter o usuário logado
            user = request.user

            # Criar e salvar a resposta no banco de dados
            models.chat_facts_onboarding_answers.objects.create(
                user=user,
                question=question,
                answer=answer,
                order=question.order  # Caso você queira armazenar a ordem das perguntas
            )

            # Retornar sucesso
            return JsonResponse({'status': 'success', 'message': 'Resposta salva com sucesso!'})

        except Exception as e:
            # Tratar erros, caso aconteçam
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)

@login_required
def check_onboarding_completed(request):
    # Verificar se o usuário tem respostas para todas as perguntas de onboarding
    unanswered_questions = models.chat_dim_onboarding_questions.objects.filter(
        active=True
    ).exclude(
        id__in=models.chat_facts_onboarding_answers.objects.filter(user=request.user).values('question_id')
    )
    
    # Se não houver perguntas não respondidas, o onboarding foi completado
    onboarding_completed = unanswered_questions.count() == 0
    
    return JsonResponse({'onboarding_completed': onboarding_completed})