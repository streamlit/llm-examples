from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserForm, LuluTrainningForm, EditUserForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from api import models
from django.views.decorators.csrf import csrf_exempt 
import openai
import os

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

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        def stream_gpt():
            result = client.chat.completions.create(
                model="gpt-4o-mini",
                store= True,
                messages=[
                    {"role": "system", "content": "Your name is Lulu, you're a friend who will help children and teenagers on their academic journeys, aiming to show the positivity of life with sweetness and sensitivity."},
                    {"role": "system", "content": "Don't return texts in portugues. You don't speak Portugues."},
                    {"role": "user", "content": question}
                ],
                stream=True
            )

            for chunk in result:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        response_server = StreamingHttpResponse(stream_gpt(), content_type="text/plain; charset=utf-8")
        response_server['Cache-Control'] = 'no-cache'
        response_server['X-Accel-Buffering'] = 'no'
        
        return response_server