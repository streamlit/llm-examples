from api.utils import get_short_term_memory, classify_sentiment, get_embedding, get_relevant_memories, transcribe_with_whisper
from api import models
from .forms import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt 
import openai
import os
import json
import markdown
import tempfile

# Create your views here.

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
def view_profile(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile') 
    else:
        form = EditUserForm(instance=request.user)
    
    return render(request, 'profile.html', {'form': form})

def view_home(request):
    return render(request, 'home.html')

##################################################################
######################### lulu sessions ##########################
##################################################################

def start_new_session(request):
    if request.user.is_authenticated:
        session = models.chat_Session.objects.create(user=request.user)
    else:
        session = models.chat_Session.objects.create(user=None)
        request.session['anon_session_id'] = session.id

    return redirect('chat_session', session_id=session.id)

@login_required
def list_chat_sessions(request):
    sessions = models.chat_Session.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'list_sessions.html', {'sessions': sessions})

def view_chat_session(request, session_id):
    session = models.chat_Session.objects.get(id=session_id)
    
    if session.user and request.user.is_authenticated:
        if session.user != request.user:
            return redirect('home')  
    elif not session.user:
        
        if request.session.get('anon_session_id') != session.id:
            return redirect('home')  

    messages = session.memories.all().order_by('date_time')
    return render(request, 'lulu.html', {'session': session, 'messages': messages})



def can_anonymous_continue(session):
    MAX_MESSAGES_ANON = 30
    return session.memories.count() < MAX_MESSAGES_ANON

##################################################################
######################### lulu chat bot ##########################
##################################################################

@csrf_exempt
def view_lulu(request):
    if request.method == 'GET':
        return render(request, 'lulu.html')
    
    elif request.method == 'POST':
        question = request.POST.get('question')
        user_id = request.user.id 
        
        recent_memory = get_short_term_memory(user_id)

        relevant_memories = get_relevant_memories(user_id, question, top_k=3)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Lulu, a friendly, empathetic assistant designed to help children and teenagers improve "
                    "their language skills in Luxembourgish, German, and French. You are positive, sensitive, supportive, "
                    "and always encourage students to learn and be confident."
                )
            }
        ]

        for mem in relevant_memories:
            messages.append({"role": "user", "content": f" {mem.user_message}"})
            if mem.chat_message:
                messages.append({"role": "assistant", "content": f" {mem.chat_message}"})
        
        messages.extend(recent_memory)

        messages.append({"role": "user", "content": question})

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        def stream_gpt():
            result = client.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:personal::BVkSVA0p",
                messages=messages,
                stream=True
            )

            response_text = ""
            for chunk in result:
                if chunk.choices and chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content

            response_text_html = markdown.markdown(text=response_text, output_format='html')

            sentiment = classify_sentiment(question)
            embedding = get_embedding(question)

            models.chat_memories.objects.create(
                user_id=request.user.id,
                user_message=question,
                user_message_sentiment=sentiment,
                chat_message=response_text,
                embedding=embedding
            )

            yield response_text_html 

        response_server = StreamingHttpResponse(stream_gpt(), content_type="text/html; charset=utf-8")
        response_server['Cache-Control'] = 'no-cache'
        response_server['X-Accel-Buffering'] = 'no'
        
        return response_server

######################### Memos and Feedback #########################

def view_save_memo(request):
    if request.method == "POST":
        texto = request.POST.get("message")
        if texto:
            user_instance = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key

            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            memo = models.facts_memos.objects.create(
                user=user_instance,
                message=texto,
                session_key=None if user_instance else session_key
            )
            return JsonResponse({"status": "ok", "memo_id": memo.id})
        return JsonResponse({"status": "error", "message": "Empty Message"}, status=400)
    return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)


@csrf_exempt
def view_delete_memo(request, memo_id):
    if request.method == "POST":
        user_instance = request.user if request.user.is_authenticated else None
        if user_instance:
            memo = models.facts_memos.objects.get(id=memo_id, user=user_instance)
        else:
            session_key = request.session.session_key
            if not session_key:
                return JsonResponse({"status": "error", "message": "Sessão não encontrada"}, status=403)
            memo = models.facts_memos.objects.get(id=memo_id, user__isnull=True, session_key=session_key)
        memo.delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=405)

def view_save_feedback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_prompt = data.get("user_prompt", "").strip()
        bot_message = data.get("bot_message", "").strip()
        feedback_type = data.get("feedback_type", "").strip()

        if not user_prompt or not bot_message or not feedback_type:
            return JsonResponse({"error": "Dados inválidos."}, status=400)
        
        user_instance = request.user if request.user.is_authenticated else None

        existing_feedback = models.chat_facts_feedback.objects.filter(
            user=user_instance,
            user_prompt=user_prompt,
            bot_message=bot_message
        ).first()

        if existing_feedback:
            if existing_feedback.feedback_type == feedback_type:
                existing_feedback.delete()
                return JsonResponse({"status": "removed"})
            else:
                existing_feedback.feedback_type = feedback_type
                existing_feedback.save()
                return JsonResponse({"status": "updated"})

        models.chat_facts_feedback.objects.create(
            user=user_instance,
            user_prompt=user_prompt,
            bot_message=bot_message,
            feedback_type=feedback_type
        )
        return JsonResponse({"status": "created"})

    return JsonResponse({"error": "Método inválido."}, status=405)

######################### Other pages #########################

def create_diary(request):
    if request.method == 'POST':
        form = diaryForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user 
            form.save()  
            return redirect('diary') 
    else:
        form = diaryForm()

    return render(request, 'diary.html', {'form': form})


######################### Onboarding #########################

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



def onboarding_data(request):
    """
    Retorna as perguntas de onboarding não respondidas em JSON com opções associadas.
    """
    
    user = request.user
    questions = models.chat_dim_onboarding_questions.objects.filter(active=True).order_by("order")
    answered_questions = models.chat_facts_onboarding_answers.objects.filter(user=user).values_list('question_id', flat=True)
    unanswered_questions = questions.exclude(id__in=answered_questions)
    options = models.chat_dim_onboarding_options_answers.objects.all()
    grouped_options = {}
    for option in options:
        if option.question.id not in grouped_options:
            grouped_options[option.question.id] = []
        grouped_options[option.question.id].append(option.option)

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

@csrf_exempt 
def save_onboarding_answer(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            question_id = data.get('question_id')
            answer = data.get('answer')

            if not question_id or answer is None:
                return JsonResponse({'status': 'error', 'message': 'Dados incompletos'}, status=400)

            question = models.chat_dim_onboarding_questions.objects.get(id=question_id)

            user = request.user

            models.chat_facts_onboarding_answers.objects.create(
                user=user,
                question=question,
                answer=answer,
                order=question.order
            )

            return JsonResponse({'status': 'success', 'message': 'Resposta salva com sucesso!'})

        except Exception as e:

            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


def check_onboarding_completed(request):
    unanswered_questions = models.chat_dim_onboarding_questions.objects.filter(
        active=True
    ).exclude(
        id__in=models.chat_facts_onboarding_answers.objects.filter(user=request.user).values('question_id')
    )
    
    onboarding_completed = unanswered_questions.count() == 0
    
    return JsonResponse({'onboarding_completed': onboarding_completed})

### Speech-to-text
@csrf_exempt
def speech_to_text_view(request):
    if request.method == "POST":
        audio_file = request.FILES['audio']
        # Use a extensão correta do arquivo original
        ext = audio_file.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        recognized_text = transcribe_with_whisper(tmp_path, language_code="lb")
        return JsonResponse({"text": recognized_text})
    return JsonResponse({"error": "Only POST supported"}, status=405)