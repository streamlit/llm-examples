from .utils import get_short_term_memory
from .forms import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt 
from django.utils.safestring import mark_safe
from api import models
import openai
import os
import json
import markdown
from django.db.models.functions import TruncDate
from django.db.models import Count

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
def view_surprise_me(request):
    return render(request, 'surprise_me.html')

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

            models.chat_memories.objects.create(
                user_id=request.user.id,
                user_message=question,
                chat_message=response_text
            )

            yield response_text_html 

        response_server = StreamingHttpResponse(stream_gpt(), content_type="text/html; charset=utf-8")
        response_server['Cache-Control'] = 'no-cache'
        response_server['X-Accel-Buffering'] = 'no'
        
        return response_server


######################### Memos and Feedback #########################
@login_required
def view_save_memo(request):
    if request.method == "POST":
        texto = request.POST.get("message")
        if texto:
            memo = models.facts_memos.objects.create(user=request.user, message=texto)
            return JsonResponse({"status": "ok", "memo_id": memo.id})
        return JsonResponse({"status": "error", "message": "Mensagem vazia"}, status=400)
    return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)

@login_required
@csrf_exempt
def view_delete_memo(request, memo_id):
    if request.method == "POST":
        memo = models.facts_memos.objects.get(id=memo_id, user=request.user)
        memo.delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=405)

@login_required
def view_chat_memos(request):
    memos = models.facts_memos.objects.filter(user=request.user).order_by("-datetime")
    return render(request, "chat_memos.html", {"memos": memos})

@login_required
def view_chat_memory(request):
    if request.user.is_authenticated:
        conversas = models.chat_memories.objects.filter(user_id=str(request.user.id))
    else:
        conversas = models.chat_memories.objects.none()

    return render(request, 'chat_memory.html', {'conversas': conversas})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def view_save_feedback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_prompt = data.get("user_prompt", "").strip()
        bot_message = data.get("bot_message", "").strip()
        feedback_type = data.get("feedback_type", "").strip()

        if not user_prompt or not bot_message or not feedback_type:
            return JsonResponse({"error": "Dados inválidos."}, status=400)

        # Verifica se já existe feedback desse usuário para esse par prompt/resposta
        existing_feedback = models.chat_facts_feedback.objects.filter(
            user=request.user,
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

        # Nenhum feedback anterior → criar novo
        models.chat_facts_feedback.objects.create(
            user=request.user,
            user_prompt=user_prompt,
            bot_message=bot_message,
            feedback_type=feedback_type
        )
        return JsonResponse({"status": "created"})

    return JsonResponse({"error": "Método inválido."}, status=405)

######################### Other pages #########################

@login_required
def view_emotions_atlas(request):
    return render(request, 'emotions_atlas.html')

@login_required
def view_ideas_box(request):
    return render(request, 'ideas_box.html')

@login_required
def view_diary(request):
    entries = models.diary_facts.objects.filter(user=request.user).order_by('-date')  
    return render(request, 'diary.html', {'entries': entries})

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

def diary_view(request):
    entries = models.diary_facts.objects.filter(user=request.user).order_by('-date')  
    return render(request, 'diary.html', {'entries': entries})


######################### Onboarding #########################
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


@login_required
def onboarding_data(request):
    """Retorna as perguntas de onboarding não respondidas em JSON com opções associadas."""
    
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

@login_required
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

@login_required
def check_onboarding_completed(request):
    unanswered_questions = models.chat_dim_onboarding_questions.objects.filter(
        active=True
    ).exclude(
        id__in=models.chat_facts_onboarding_answers.objects.filter(user=request.user).values('question_id')
    )
    
    onboarding_completed = unanswered_questions.count() == 0
    
    return JsonResponse({'onboarding_completed': onboarding_completed})

######################### Question suggestion based on chat context #########################
@login_required
def generate_suggestions(request):
    user_id = request.user.id

    recent_messages = models.chat_memories.objects.filter(user_id=user_id).order_by('-id')[:3]
    system_prompt = (
        "You are a smart assistant responsible for generating follow-up short question suggestions, max 12 tokens."
        "based on the conversation between the user and an AI assistant named Lulu.\n\n"
        "Your goal is to suggest 3 to 5 natural, context-aware questions the user might ask Lulu about himself next. These questions should:\n"
        "- Be written **from the user's perspective**, as if the user is talking about their own life, needs, problems, or interests.\n"
        "- Focus on the user's goals, doubts, and context — **not about Lulu or her experiences**.\n"
        "- Use natural, informal, curious phrasing (e.g. 'How can I...', 'What should I do if...', 'Can you help me with...').\n"
        "- Feel natural, informal, and curious — as if coming from the user to learn or go deeper into the subject, always with the user as the focus.\n"
        "- Be relevant to the conversation history provided.\n"
        "- Be safe and appropriate for a general-purpose assistant.\n\n"
        "- Encourage the continuation or deepening of the conversation.\n\n"
        "IMPORTANT: Do NOT generate questions that are:\n"
        "- Sexual, explicit, flirtatious, discriminatory, or offensive\n"
        "- About politics, religion, or medical advice\n\n"
        "Use the conversation history to generate your suggestions."
    )
    messages = [
        {
            "role": "system", 
            "content": system_prompt
        }
    ]

    for msg in reversed(recent_messages):
        messages.append({"role": "user", "content": msg.user_message})
        messages.append({"role": "assistant", "content": msg.chat_message})

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + [
            {
                "role": "user", 
                "content": "Generate a short question suggestion to continue this conversation, maintaining the context of the dialogue and the just use english language. Just return the question."
            }
        ],
        max_tokens=12,
        temperature = 1.4,
        n=3
    )

    suggestions = [choice.message.content.strip() for choice in response.choices]

    return JsonResponse({"suggestions": suggestions})

######################### Am I Boring Foms #########################
@login_required
@staff_member_required
def view_management_am_i_boring_questions(request):
     
    if request.method == 'POST':
        form = amIBoringQuestionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('adm_am_i_boring_questions')
    else:
        form = amIBoringQuestionForm()
    
    questions = models.dim_am_i_boring_questions.objects.prefetch_related("boring_options").order_by("order")
    return render(request,'adm_am_i_boring.html',{'questions': questions, 'form':form})

@login_required
@staff_member_required
@csrf_exempt
def add_option_am_i_boring(request):
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = data.get("question_id")
        option_text = data.get("option")

        question = models.dim_am_i_boring_questions.objects.get(id=question_id)
        new_option = models.dim_am_i_boring_options_answers.objects.create(question=question, option=option_text)
        new_option.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@csrf_exempt
def delete_option_am_i_boring(request, option_id):
    if request.method == "DELETE":
        try:
            option = models.dim_am_i_boring_options_answers.objects.get(id=option_id)
            option.delete()
            return JsonResponse({"success": True})
        except models.dim_am_i_boring_options_answers.DoesNotExist:
            return JsonResponse({"success": False}, status=404)

    return JsonResponse({"success": False}, status=400)

@login_required
def am_i_boring_data(request):
    """Retorna todas as perguntas ativas em JSON com opções associadas, mesmo que já tenham sido respondidas."""
    
    user = request.user

    questions = models.dim_am_i_boring_questions.objects.filter(active=True).order_by("order")

    options = models.dim_am_i_boring_options_answers.objects.filter(question__in=questions)

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
            for question in questions
        ]
    }

    return JsonResponse(data)

@login_required
@staff_member_required
def update_question_active_am_i_boring(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            active = data.get('active')
            question = models.dim_am_i_boring_questions.objects.get(id=id)
            question.active = active
            question.save()
            return JsonResponse({'success': True})
        except models.dim_am_i_boring_questions.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def view_dim_am_i_boring_questions(request):
    questions = models.dim_am_i_boring_questions.objects.all().prefetch_related("options")
    return render(request, "adm_am_i_boring.html", {"questions": questions})

@login_required
@csrf_exempt 
def save_am_i_boring_answer(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            question_id = data.get('question_id')
            answer = data.get('answer')

            if not question_id or answer is None:
                return JsonResponse({'status': 'error', 'message': 'Dados incompletos'}, status=400)

            question = models.dim_am_i_boring_questions.objects.get(id=question_id)

            user = request.user

            models.facts_am_i_boring_answers.objects.create(
                user=user,
                question=question,
                answer=answer,
                order=question.order
            )

            return JsonResponse({'status': 'success', 'message': 'Resposta salva com sucesso!'})

        except Exception as e:

            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


###### Dashboards #####

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import TruncDate

@login_required
def dashboard_view(request):
    
    # --- CHAT ---
    chat_per_day = (
        models.chat_memories.objects
        .annotate(date=TruncDate('date_time'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    chat_dates = [str(r['date']) for r in chat_per_day]
    chat_counts = [r['count'] for r in chat_per_day]

    top_users_chat = (
        models.chat_memories.objects
        .values('user_id')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    top_usernames = []
    top_user_counts = []
    from django.contrib.auth.models import User
    for u in top_users_chat:
        user = User.objects.get(id=u['user_id'])
        top_usernames.append(user.username)
        top_user_counts.append(u['count'])

    total_messages = models.chat_memories.objects.count()

    # --- ONBOARDING ---
    total_questions = models.chat_dim_onboarding_questions.objects.filter(active=True).count()
    total_users = User.objects.count()
    completed_users = 0
    for user in User.objects.all():
        answered = models.chat_facts_onboarding_answers.objects.filter(user=user).count()
        if answered >= total_questions:
            completed_users += 1
    onboarding_completion = round((completed_users / total_users) * 100 if total_users > 0 else 0, 2)

    answers_count = (
        models.chat_facts_onboarding_answers.objects
        .values('question__question')
        .annotate(count=Count('id'))
    )
    onboarding_questions = [r['question__question'] for r in answers_count]
    onboarding_counts = [r['count'] for r in answers_count]

    # --- FEEDBACK ---
    feedbacks = (
        models.chat_facts_feedback.objects
        .values('feedback_type')
        .annotate(count=Count('id'))
    )
    likes = next((f['count'] for f in feedbacks if f['feedback_type'] == 'like'), 0)
    dislikes = next((f['count'] for f in feedbacks if f['feedback_type'] == 'dislike'), 0)
    total_feedbacks = likes + dislikes
    
    

    reasons = (
        models.chat_facts_feedback.objects
        .filter(feedback_type='dislike')
        .values('reason')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    reasons_texts = [r['reason'] or "Sem motivo" for r in reasons]
    reasons_counts = [r['count'] for r in reasons]

    unique_users = (
    models.chat_memories.objects
    .annotate(date=TruncDate('date_time'))
    .values('date')
    .annotate(unique_count=Count('user_id', distinct=True))
    .order_by('date')
    )

    unique_user_dates = [str(u['date']) for u in unique_users]
    unique_user_counts = [u['unique_count'] for u in unique_users]

    return render(request, 'dashboard.html', {
        # Chat
        'chat_dates_json': json.dumps(chat_dates),
        'chat_counts_json': json.dumps(chat_counts),
        'top_usernames_json': json.dumps(top_usernames),
        'top_user_counts_json': json.dumps(top_user_counts),
        'total_messages': total_messages,

        # Onboarding
        'onboarding_completion': onboarding_completion,
        'onboarding_questions_json': json.dumps(onboarding_questions),
        'onboarding_counts_json': json.dumps(onboarding_counts),

        # Feedback
        'likes': likes,
        'dislikes': dislikes,
        'total_feedbacks': total_feedbacks,
        'reasons_texts_json': json.dumps(reasons_texts),
        'reasons_counts_json': json.dumps(reasons_counts),

        'unique_user_dates_json': json.dumps(unique_user_dates),
        'unique_user_counts_json': json.dumps(unique_user_counts),
    })

