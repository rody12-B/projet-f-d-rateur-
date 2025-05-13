from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta




#Creation des classes pour representer les models dans la base de donnnees

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_publisher = models.BooleanField(default=False)
   

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class Book(models.Model):
    GENRE_CHOICES = [
        ('roman', 'Roman'),
        ('poesie', 'Poésie'),
        ('science', 'Science'),
        ('informatique', 'Informatique'),
        ('histoire', 'Histoire'),
        ('biographie', 'Biographie'),
        ('autre', 'Autre'),
    ]
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    publisher = models.CharField(max_length=200)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='autre') 
    desc = models.CharField(max_length=1000)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    pdf = models.FileField(upload_to='bibliotheque/pdfs/')
    cover = models.ImageField(upload_to='bibliotheque/covers/', null=True, blank=True)
    disponible = models.BooleanField(default=True)
    views = models.IntegerField(default=0) 
    
    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.pdf.delete()
        self.cover.delete()
        super().delete(*args, **kwargs)        


def default_date_limite():
    return timezone.now().date() + timedelta(days=14)

class Emprunt(models.Model):
    lecteur = models.ForeignKey(User, on_delete=models.CASCADE)
    livre = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_emprunt = models.DateField(default=timezone.now)
    date_limite = models.DateField(default=default_date_limite)  
    date_retour = models.DateField(null=True, blank=True)
    rendu = models.BooleanField(default=False)
    confirme = models.BooleanField(default=False)
    annule = models.BooleanField(default=False)
    date_retour = models.DateTimeField(null=True, blank=True)
    

    def est_en_retard(self):
        return not self.rendu and timezone.now().date() > self.date_limite
    
    @property
    def penalite(self):
        if self.est_en_retard():
            jours_retard = (timezone.now().date() - self.date_limite).days
            return jours_retard * 1
        return 0
    
    def save(self, *args, **kwargs):
        """Mise à jour automatique du statut"""
        super().save(*args, **kwargs)


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        return str(self.message)



class DeleteRequest(models.Model):
    delete_request = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.delete_request


class Feedback(models.Model):
    feedback = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.feedback
    

class Rapport(models.Model):
    TYPE_CHOICES = [
        ('POPULARITE', 'Livres les plus populaires'),
        ('RETARDS', 'Retards fréquents'),
        ('HISTORIQUE', 'Historique utilisateur')
    ]
    type_rapport = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_generation = models.DateTimeField(auto_now_add=True)
    contenu = models.JSONField()  # Pour stocker les données du rapport
    genere_par = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_type_rapport_display()} - {self.date_generation}"
    
class Borrow(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('ended', 'Terminé'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
