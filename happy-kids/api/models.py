from django.db import models
from django.contrib.auth.models import User

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

class chat_memories(models.Model):
    user_id = models.CharField(max_length=100)
    user_message = models.TextField()
    chat_message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)

class dim_question_type(models.Model):
    question_type = models.TextField(unique=True)

    def __str__(self):
        return self.question_type

class chat_dim_onboarding_questions(models.Model):
    question = models.TextField()
    question_type = models.ForeignKey(dim_question_type, on_delete=models.CASCADE, null=True)
    order = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

class chat_dim_onboarding_options_answers(models.Model):
    question = models.ForeignKey(chat_dim_onboarding_questions, on_delete=models.CASCADE,related_name="options")
    option = models.TextField()

    def __str__(self):
        return f"{self.question} - {self.option}"
    
class chat_facts_onboarding_answers(models.Model):
    user = models.ForeignKey("auth.User",on_delete=models.CASCADE)
    question  = models.ForeignKey(chat_dim_onboarding_questions, on_delete=models.CASCADE)
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