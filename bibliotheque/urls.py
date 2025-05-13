from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


#urls partagées 

urlpatterns = [

# Shared URL's
 path('', views.login_form, name='home'),
 path('login/', views.loginView, name='login'),
 path('logout/', views.logoutView, name='logout'),
 path('regform/', views.register_form, name='regform'),
 path('register/', views.registerView, name='register'),





 # Publisher URL's
 path('public/', views.public, name='public'),
 path('Carousel/', views.Carousel, name='Carousel'),
 path('livres/', views.UBookListView.as_view(), name='livres'),
 path('uabook_form/', views.uabook_form, name='uabook_form'),
 path('uabook/', views.uabook, name='uabook'),
 path('historique/', views.mes_historiques, name='historique'),
 path('ucchat/', views.UCreateChat.as_view(), name='ucchat'),
 path('ulchat/', views.UListChat.as_view(), name='ulchat'),
 path('request_form/', views.request_form, name='request_form'),
 path('delete_request/', views.delete_request, name='delete_request'),
 path('uprofil/', views.uprofil, name='uprofil'),
 path('uvbook/<int:pk>', views.UViewBook.as_view(), name='uvbook'),
 path('udvbook/<int:pk>', views.UDViewBook.as_view(), name='udvbook'),
 path('send_feedback/', views.send_feedback, name='send_feedback'),
 path('update_profile/', views.update_profile, name='update_profile'),
 path('livre/<int:livre_id>/emprunter/', views.emprunter_livre, name='emprunter_livre'),
 path('retourner_livre/<int:emprunt_id>/', views.retourner_livre_utilisateur, name='retourner_livre'),
 path('annuler-emprunt/<int:emprunt_id>/', views.annuler_emprunt_utilisateur, name='annuler_emprunt'),
 path('mes_emprunts/', views.mes_emprunts, name='mes_emprunts'),
 path('livres/<int:pk>/', UViewBook.as_view(), name='livre_detail'),
 path('recommandations/', views.recommandations_utilisateur, name='recommandations'),
 path('usearch/', views.usearch, name='usearch'),



 # Admin URL's
 path('dashboard/', views.dashboard, name='dashboard'),
 path('acchat/', views.ACreateChat.as_view(), name='acchat'),
 path('alchat/', views.AListChat.as_view(), name='alchat'),
 path('aabook_form/', views.aabook_form, name='aabook_form'),
 path('aabook/', views.aabook, name='aabook'),
 path('albook/', views.ABookListView.as_view(), name='albook'),
 path('ambook/', views.AManageBook.as_view(), name='ambook'),
 path('adbook/<int:pk>', views.ADeleteBook.as_view(), name='adbook'),
 path('avbook/<int:pk>', views.AViewBook.as_view(), name='avbook'),
 path('aebook/<int:pk>', views.AEditView.as_view(), name='aebook'),
 path('adrequest/', views.ADeleteRequest.as_view(), name='adrequest'),
 path('aprofil/', views.Aprofil, name='profil'),
 path('aupdate_profile/', views.Aupdate_profile, name='update_profile'),
 path('rapports/<str:rapport_type>/', views.generer_rapport, name='generer_rapport'),
 path('emprunts_utilisateurs/', views.emprunts_utilisateurs, name='emprunts_utilisateurs'),
 path('confirmer-emprunt/<int:emprunt_id>/', views.confirmer_emprunt, name='confirmer_emprunt'),
 path('annuler-emprunt/<int:emprunt_id>/', views.annuler_emprunt, name='annuler_emprunt'),
 path('asearch/', views.asearch, name='asearch'),
 path('adbookk/<int:pk>', views.ADeleteBookk.as_view(), name='adbookk'),
 path('create_user_form/', views.create_user_form, name='create_user_form'),
 path('aluser/', views.ListUserView.as_view(), name='aluser'),
 path('create_use/', views.create_user, name='create_user'),
 path('alvuser/<int:pk>', views.ALViewUser.as_view(), name='alvuser'),
 path('aeuser/<int:pk>', views.AEditUser.as_view(), name='aeuser'),
 path('aduser/<int:pk>', views.ADeleteUser.as_view(), name='aduser'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)