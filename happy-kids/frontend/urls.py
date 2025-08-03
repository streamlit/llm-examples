from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_home, name='home'),

    path('chat/start/', views.start_new_session, name='start_new_session'),
    path('chat/sessao/<int:session_id>/', views.view_chat_session, name='chat_session'),
    path('chat/sessoes/', views.list_chat_sessions, name='list_chat_sessions'),

    path('lulu', views.view_lulu, name='lulu'),
    path('adm/users_page', views.view_users, name='users_page'),
    path('profile', views.view_profile, name='profile'),

    path('update-question-active/<int:id>/', views.update_question_active, name='update_question_active'),
    path('add_option/', views.add_option, name="add_option"),
    path('delete_option/<int:option_id>/', views.delete_option, name="delete_option"),

    path('save_memos/', views.view_save_memo, name='save_memos'),
    path('delete_memo/<int:memo_id>/', views.view_delete_memo, name="delete_memo"),
    path("save_feedback/", views.view_save_feedback, name="save_feedback"),

    path('create_diary/', views.create_diary, name='create_diary'),
    path("generate_suggestions/", views.generate_suggestions, name="generate_suggestions"),

    path('speech-to-text/', views.speech_to_text_view, name='speech_to_text'),

]