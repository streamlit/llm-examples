from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class historicalSessions(models.Model):
    sessionDate = models.DateTimeField("session date", default="")
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

class luluTrainning(models.Model):
    version_title = models.CharField(max_length=255)
    attachments = models.FileField(upload_to='uploads/%Y/%m/%d/')
    comments = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)

class UsersMilestones(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    milestone = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class chat_Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, default="Nova Sessão")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.user:
            return f"{self.title} ({self.user.username})"
        else:
            return f"{self.title} (Anônimo)"
    
class chat_memories(models.Model):
    session = models.ForeignKey(chat_Session, on_delete=models.CASCADE, related_name='memories', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_message = models.TextField()
    user_message_sentiment = models.CharField(max_length=20, blank=True, null=True) 
    chat_message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    embedding = ArrayField(models.FloatField(), blank=True, null=True) 

class dim_question_type(models.Model):
    question_type = models.TextField(unique=True)

    def __str__(self):
        return self.question_type

class chat_dim_onboarding_questions(models.Model):
    question = models.TextField()
    question_type = models.ForeignKey(dim_question_type, on_delete=models.CASCADE, null=True, related_name="onboarding_question_types")
    order = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

class chat_dim_onboarding_options_answers(models.Model):
    question = models.ForeignKey(chat_dim_onboarding_questions, on_delete=models.CASCADE, related_name="onboarding_options")
    option = models.TextField()

    def __str__(self):
        return f"{self.question} - {self.option}"
    
class chat_facts_onboarding_answers(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    question  = models.ForeignKey(chat_dim_onboarding_questions, on_delete=models.CASCADE, related_name="onboarding_answers")
    answer = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.id} | {self.question.id} | {self.question.order} | {self.answer}"

class diary_facts(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.title

class dim_am_i_boring_questions(models.Model):
    question = models.TextField()
    question_type = models.ForeignKey(dim_question_type, on_delete=models.CASCADE, null=True, related_name="boring_question_types")
    order = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

class dim_am_i_boring_options_answers(models.Model):
    question = models.ForeignKey(dim_am_i_boring_questions, on_delete=models.CASCADE, related_name="boring_options")
    option = models.TextField()

    def __str__(self):
        return f"{self.question} - {self.option}"
    
class facts_am_i_boring_answers(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    question  = models.ForeignKey(dim_am_i_boring_questions, on_delete=models.CASCADE, related_name="boring_answers")
    answer = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.id} | {self.question.id} | {self.question.order} | {self.answer}"
    
class facts_memos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Memo de {self.user.username} em {self.datetime.strftime('%d/%m/%Y %H:%M')}"

class chat_facts_feedback(models.Model):
    user_prompt = models.TextField()
    bot_message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    feedback_type = models.CharField(
        max_length=20,
        choices=[("like", "Like"), ("dislike", "Dislike")]
    )
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bot_message