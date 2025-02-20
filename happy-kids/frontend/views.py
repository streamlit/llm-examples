from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserForm, LuluTrainningForm, EditUserForm, questionForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from api import models
from django.views.decorators.csrf import csrf_exempt 
import openai
import os
from .utils import get_short_term_memory, save_short_term_memory

import markdown
from django.utils.safestring import mark_safe

# Create your views here.
@login_required
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
def view_training_files(request):
    return render(request, 'trainingFiles.html')

@login_required
def view_profile(request):
    return render(request, 'profile.html')

@login_required
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
    
def view_chat_memory(request):
    if request.user.is_authenticated:
        conversas = models.chat_memories.objects.filter(user_id=str(request.user.id))
    else:
        conversas = models.chat_memories.objects.none()

    return render(request, 'chat_memory.html', {'conversas': conversas})

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