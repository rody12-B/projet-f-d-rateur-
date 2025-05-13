from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from bootstrap_modal_forms.mixins import PassRequestMixin
from .models import User, Book, Chat, DeleteRequest, Feedback 
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import ChatForm, BookForm, UserForm
from .models import User, Book, Chat, DeleteRequest, Feedback, Emprunt,Rapport, Borrow
import operator
import itertools
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, F
from django.contrib.auth.decorators import permission_required
from .pdf_utils import generate_rapport_pdf
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q 




# Shared Views
def login_form(request):
	return render(request, 'auth/login.html')


def logoutView(request):
	logout(request)
	return redirect('home')



def admin_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and (u.is_admin or u.is_superuser),
        login_url='home'  
    )(view_func)
    return decorated_view_func


def loginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
			if user.is_admin or user.is_superuser:
				return redirect('dashboard')
			else:
			    return redirect('public')
		else:
		    messages.info(request, "Invalid username or password")
		    return redirect('home')


def register_form(request):
	return render(request, 'auth/register.html')


def registerView(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		password = make_password(password)

		a = User(username=username, email=email, password=password)
		a.save()
		messages.success(request, 'Account was created successfully')
		return redirect('home')
	else:
	    messages.error(request, 'Registration fail, try again later')
	    return redirect('regform')

			


# Public views
@login_required
def publisher(request):
	return render(request, 'public/home.html')



@login_required
def public(request):
    user = request.user

    emprunts_pending = Emprunt.objects.filter(lecteur=user, confirme=False, annule=False, rendu=False)
    emprunts_confirmed = Emprunt.objects.filter(lecteur=user, confirme=True, rendu=False)
    emprunts_ended = Emprunt.objects.filter(lecteur=user, rendu=True)

    return render(request, 'public/public.html', {
        'emprunts_pending': emprunts_pending,
        'emprunts_confirmed': emprunts_confirmed,
        'emprunts_ended': emprunts_ended,
    })


@login_required
def uabook_form(request):
	return render(request, 'public/add_book.html')


@login_required
def request_form(request):
	return render(request, 'public/mes_emprunts.html')


@login_required
def uprofil(request):
	return render(request, 'public/profil.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        user = request.user
        user.username = name
        user.email = email

        # Vérifier si l'ancien mot de passe est correct
        if user.check_password(old_password):
            # Mettre à jour le mot de passe s'il est fourni
            if new_password:  
                user.set_password(new_password)
                # Met à jour la session de l'utilisateur pour éviter la déconnexion
                update_session_auth_hash(request, user)
            user.save()
            messages.success(request, 'Profil mis à jour avec succès!')
        else:
            messages.error(request, 'L\'ancien mot de passe est incorrect.')

        return redirect('profil') 

    return render(request, 'public/update_profil.html')  


@login_required
def usearch(request):
    query = request.GET['query']
    print(type(query))


    #data = query.split()
    data = query
    print(len(data))
    if( len(data) == 0):
        return redirect('public')
    else:
                a = data

                # Searching for It
                qs5 =models.Book.objects.filter(id__iexact=a).distinct()
                qs6 =models.Book.objects.filter(id__exact=a).distinct()

                qs7 =models.Book.objects.all().filter(id__contains=a)
                qs8 =models.Book.objects.select_related().filter(id__contains=a).distinct()
                qs9 =models.Book.objects.filter(id__startswith=a).distinct()
                qs10 =models.Book.objects.filter(id__endswith=a).distinct()
                qs11 =models.Book.objects.filter(id__istartswith=a).distinct()
                qs12 =models.Book.objects.all().filter(id__icontains=a)
                qs13 =models.Book.objects.filter(id__iendswith=a).distinct()




                files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

                res = []
                for i in files:
                    if i not in res:
                        res.append(i)


                # word variable will be shown in html when user click on search button
                word="Aucun résultat trouvé ! :"
                print("Result")

                print(res)
                files = res




                page = request.GET.get('page', 1)
                paginator = Paginator(files, 10)
                try:
                    files = paginator.page(page)
                except PageNotAnInteger:
                    files = paginator.page(1)
                except EmptyPage:
                    files = paginator.page(paginator.num_pages)
   


                if files:
                    return render(request,'public/result.html',{'files':files,'word':word})
                return render(request,'public/result.html',{'files':files,'word':word})
            

def Carousel(request):
    MIN_CAROUSEL_BOOKS = 3  # Minimum de livres pour afficher le carrousel
    
    all_books = Book.objects.all()
    book_count = all_books.count()
    
    # Livres populaires (par vues ou tous les livres si pas assez de vues)
    popular_books = list(
        all_books.order_by('-views')[:6] if book_count >= MIN_CAROUSEL_BOOKS 
        else all_books[:6]
    )
    
    # Recommandations (aléatoires mais différents des populaires si possible)
    remaining_books = all_books.exclude(id__in=[b.id for b in popular_books]) if popular_books else all_books
    recommandations = list(
        remaining_books.order_by('?')[:4] if remaining_books.exists() 
        else popular_books[:4]  # Fallback si pas assez de livres différents
    )
    
    return render(request, 'home.html', {
        'popular_books': popular_books,
        'recommandations': recommandations,
        'show_carousel': book_count >= MIN_CAROUSEL_BOOKS
    })
 
            
@login_required
def recommandations_utilisateur(request):
    # Étape 1 : Collecte des emprunts
    emprunts = Emprunt.objects.all().select_related('lecteur', 'livre')

    data = []
    for emp in emprunts:
        data.append({
            'user_id': emp.lecteur.id,
            'livre_id': emp.livre.id,
            'title': emp.livre.title
        })

    print("Données récupérées :", data)  # Débogage

    if not data:
        return render(request, 'public/recommandations.html', {'recommandations': []})

    df = pd.DataFrame(data)

    # Étape 2 : Création de la matrice utilisateur-livre
    pivot = pd.pivot_table(df, index='user_id', columns='livre_id', aggfunc='count', fill_value=0)
    print("Matrice utilisateur-livre :", pivot)  # Débogage

    # Étape 3 : Calcul de la similarité
    try:
        similarity = cosine_similarity(pivot)
        similarity_df = pd.DataFrame(similarity, index=pivot.index, columns=pivot.index)
    except Exception as e:
        print("Erreur lors du calcul de similarité :", e)  # Débogage
        return render(request, 'public/recommandations.html', {'recommandations': []})

    current_user_id = request.user.id
    if current_user_id not in similarity_df.index:
        return render(request, 'public/recommandations.html', {'recommandations': []})

    similar_users = similarity_df[current_user_id].sort_values(ascending=False).drop(current_user_id)

    # Étape 4 : Génération des recommandations
    livres_lus = set(df[df['user_id'] == current_user_id]['livre_id'])
    livres_recommandes = set()

    for user_id in similar_users.index:
        livres = set(df[df['user_id'] == user_id]['livre_id'])
        livres_recommandes |= (livres - livres_lus)
        if len(livres_recommandes) >= 10:
            break

    print("Livres recommandés :", livres_recommandes)  # Débogage

    livres = Book.objects.filter(id__in=livres_recommandes)

    return render(request, 'public/recommandations.html', {'recommandations': livres})


@login_required
def annuler_emprunt_utilisateur(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_id, lecteur=request.user)
    
    if emprunt.rendu:
        messages.error(request, "Cet emprunt a déjà été retourné.")
    elif emprunt.annule:
        messages.error(request, "Cet emprunt a déjà été annulé.")
    elif emprunt.confirme:
        messages.error(request, "Cet emprunt a déjà été confirmé, vous ne pouvez plus l'annuler.")
    else:
        emprunt.annule = True
        emprunt.livre.disponible = True
        emprunt.save()
        emprunt.livre.save()
        messages.success(request, f"L'emprunt de '{emprunt.livre.title}' a été annulé avec succès.")
    
    return redirect('mes_emprunts')  # Changement de redirection

@login_required
def emprunter_livre(request, livre_id):
    livre = get_object_or_404(Book, pk=livre_id)
    if livre.disponible:
        # Vérifie si l'utilisateur a déjà une demande en attente pour ce livre
        if Emprunt.objects.filter(lecteur=request.user, livre=livre, confirme=False, annule=False).exists():
            messages.warning(request, "Vous avez déjà une demande en attente pour ce livre.")
        else:
            emprunt = Emprunt(lecteur=request.user, livre=livre)
            emprunt.save()
            livre.disponible = False
            livre.save()
            messages.success(request, "Demande d'emprunt envoyée. En attente de validation.")
    else:
        messages.error(request, "Livre indisponible.")
    return redirect('livres')

@login_required
def retourner_livre_utilisateur(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_id, lecteur=request.user)
    
    if emprunt.rendu:
        messages.error(request, "Ce livre a déjà été retourné.")
    elif emprunt.annule:
        messages.error(request, "Cet emprunt a été annulé, vous ne pouvez pas le retourner.")
    elif not emprunt.confirme:
        messages.error(request, "Cet emprunt n'a pas été confirmé, vous ne pouvez pas le retourner.")
    else:
        emprunt.rendu = True
        emprunt.date_retour = timezone.now()  # Enregistrer la date de retour
        emprunt.livre.disponible = True
        emprunt.save()
        emprunt.livre.save()
        messages.success(request, f"Le livre '{emprunt.livre.title}' a été retourné avec succès.")
    
    return redirect('mes_emprunts')



@login_required
def mes_emprunts(request):
    # Redirige vers la vue mes_historiques qui gère tout
    return redirect('historique')


@login_required
def delete_request(request):
	if request.method == 'POST':
		book_id = request.POST['delete_request']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		user_request = username + "  want book with id  " + book_id + " to be deleted"

		a = DeleteRequest(delete_request=user_request)
		a.save()
		messages.success(request, 'Request was sent')
		return redirect('request_form')
	else:
	    messages.error(request, 'Request was not sent')
	    return redirect('request_form')



@login_required
def send_feedback(request):
	if request.method == 'POST':
		feedback = request.POST['feedback']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		feedback = username + " " + " says " + feedback

		a = Feedback(feedback=feedback)
		a.save()
		messages.success(request, 'Feedback was sent')
		return redirect('feedback_form')
	else:
	    messages.error(request, 'Feedback was not sent')
	    return redirect('feedback_form')


class UViewBook(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'public/book_detail.html'

    def get_object(self, queryset=None):
        book = super().get_object(queryset)
        book.views += 1
        book.save(update_fields=['views'])  
        return book

class UDViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'public/book_d.html'


class UBookListView(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'public/book_list.html'
	context_object_name = 'books'
	paginate_by = 2

	def get_queryset(self):
		return Book.objects.order_by('-id')

@login_required
def mes_historiques(request):
    # Récupère tous les emprunts confirmés (validés par admin)
    emprunts_confirmed = Emprunt.objects.filter(
    lecteur=request.user,
    confirme=True,
    rendu=False,
    annule=False
    ).select_related('livre')
    
    # Récupère les emprunts en attente
    emprunts_pending = Emprunt.objects.filter(
        lecteur=request.user,
        confirme=False,
        annule=False
    ).select_related('livre')
    
    # Récupère les emprunts terminés (rendus ou annulés)
    emprunts_ended = Emprunt.objects.filter(
        lecteur=request.user,
    ).filter(
        Q(rendu=True) | Q(annule=True)
    ).select_related('livre')
    
    return render(request, 'public/historique.html', {
        'emprunts_confirmed': emprunts_confirmed,
        'emprunts_pending': emprunts_pending,
        'emprunts_ended': emprunts_ended
    })

@login_required
def uabook(request):
	if request.method == 'POST':
		title = request.POST['title']
		author = request.POST['author']
		year = request.POST['year']
		publisher = request.POST['publisher']
		desc = request.POST['desc']
		cover = request.FILES['cover']
		pdf = request.FILES['pdf']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username

		a = Book(title=title, author=author, year=year, publisher=publisher, 
			desc=desc, cover=cover, pdf=pdf, uploaded_by=username, user_id=user_id)
		a.save()
		messages.success(request, 'Book was uploaded successfully')
		return redirect('publisher')
	else:
	    messages.error(request, 'Book was not uploaded successfully')
	    return redirect('uabook_form')	



class UCreateChat(LoginRequiredMixin, CreateView):
	form_class = ChatForm
	model = Chat
	template_name = 'public/chat_form.html'
	success_url = reverse_lazy('ulchat')


	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.user = self.request.user
		self.object.save()
		return super().form_valid(form)


class UListChat(LoginRequiredMixin, ListView):
	model = Chat
	template_name = 'public/chat_list.html'

	def get_queryset(self):
		return Chat.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')




# Admin views

@admin_required
def dashboard(request):
    total_books = Book.objects.count()
    total_users = User.objects.filter(is_admin=False).count()
    total_emprunts = Emprunt.objects.count()

    # Emprunts en attente
    emprunts_attente = Emprunt.objects.filter(confirme=False, annule=False, rendu=False).count()

    # Statistiques pour les graphiques
    genres = Book.objects.values('genre').annotate(count=Count('emprunt')).order_by('-count')
    confirmes = Emprunt.objects.filter(confirme=True).count()
    non_confirmes = Emprunt.objects.filter(confirme=False).count()

    context = {
        'book': total_books,
        'user': total_users,
        'emprunt': total_emprunts,
        'attente': emprunts_attente,
        'genres_labels': [g['genre'].capitalize() for g in genres],
        'genres_data': [g['count'] for g in genres],
        'confirme_data': [confirmes, non_confirmes],
    }
    return render(request, 'dashboard/home.html', context)


@admin_required
def create_user_form(request):
    choice = ['0', '1', 'Publisher', 'Admin']
    choice = {'choice': choice}

    return render(request, 'dashboard/add_user.html', choice)


class ADeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name='dashboard/confirm_delete3.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully deleted"


class AEditUser( SuccessMessageMixin, UpdateView): 
    model = User
    form_class = UserForm
    template_name = 'dashboard/edit_user.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully updated"


class ListUserView(generic.ListView):
    model = User
    template_name = 'dashboard/list_users.html'
    context_object_name = 'users'
    paginate_by = 4

    def get_queryset(self):
        return User.objects.order_by('-id')
 
@admin_required
def Aprofil(request):
	return render(request, 'dashboard/profil.html')
    
@admin_required
def Aupdate_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        user = request.user
        user.username = name
        user.email = email

        # Vérifier si l'ancien mot de passe est correct
        if user.check_password(old_password):
            # Mettre à jour le mot de passe s'il est fourni
            if new_password:  
                user.set_password(new_password)
                # Met à jour la session de l'utilisateur pour éviter la déconnexion
                update_session_auth_hash(request, user)
            user.save()
            messages.success(request, 'Profil mis à jour avec succès!')
        else:
            messages.error(request, 'L\'ancien mot de passe est incorrect.')

        return redirect('profil') 

    return render(request, 'dashboard/update_profil.html')  

@admin_required
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)
        userType = request.POST['role']  
        
        if userType == "is_publisher":
            a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_publisher=True)
        elif userType == "is_admin":
            a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_admin=True)
        else:
            messages.error(request, 'Rôle non valide')
            return redirect('create_user_form')

        a.save()
        messages.success(request, 'Membre créé avec succès!')
        return redirect('aluser')
    else:
        return redirect('create_user_form')


class ALViewUser(DetailView):
    model = User
    template_name='dashboard/user_detail.html'



class ACreateChat(LoginRequiredMixin, CreateView):
	form_class = ChatForm
	model = Chat
	template_name = 'dashboard/chat_form.html'
	success_url = reverse_lazy('alchat')


	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.user = self.request.user
		self.object.save()
		return super().form_valid(form)



@admin_required
def generer_rapport(request, rapport_type):
    if rapport_type not in ['popularite', 'retards']:
        return HttpResponseBadRequest("Type de rapport invalide")

    # Gestion de l'export PDF
    if request.GET.get('export') == 'pdf':
        if rapport_type == 'popularite':
            data = Emprunt.objects.values('livre__title').annotate(
                total=Count('id')
            ).order_by('-total')[:10]
            title = "Livres populaires"
        else:
            data = Emprunt.objects.filter(
                date_limite__lt=timezone.now().date(),
                rendu=False
            ).values('lecteur__username').annotate(
                retards=Count('id')
            ).order_by('-retards')
            title = "Retards fréquents"
        
        pdf_buffer = generate_rapport_pdf(data, title)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_{rapport_type}.pdf"'
        return response

    # Logique existante...
    if rapport_type == 'popularite':
        data = Emprunt.objects.values('livre__title','livre__genre').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        return render(request, 'dashboard/rapport.html', {
            'rapport': {'type_rapport': 'popularite', 'date_generation': timezone.now()},
            'data': data
        })
    else:
        data = Emprunt.objects.filter(
            date_limite__lt=timezone.now().date(),
            rendu=False
        ).values('lecteur__username').annotate(
            retards=Count('id')
        ).order_by('-retards')
        
        rapport = Rapport.objects.create(
            type_rapport=rapport_type.upper(),
            contenu=list(data),
            genere_par=request.user
        )
        
        return render(request, 'dashboard/rapport.html', {
            'rapport': rapport,
            'data': data
        })



class AListChat(LoginRequiredMixin, ListView):
	model = Chat
	template_name = 'dashboard/chat_list.html'

	def get_queryset(self):
		return Chat.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


@admin_required
def aabook_form(request):
	return render(request, 'dashboard/add_book.html')


@admin_required
def aabook(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        genre = request.POST['genre'] 
        desc = request.POST['desc']
        cover = request.FILES['cover']
        pdf = request.FILES['pdf']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username

        a = Book(title=title, author=author, year=year, publisher=publisher, genre=genre,
                  desc=desc, cover=cover, pdf=pdf, uploaded_by=username, user_id=user_id)
        a.save()
        messages.success(request, 'Livre ajouté avec succès')
        return redirect('ambook')
    else:
        messages.error(request, 'Livre téléchargé avec succès')
        return redirect('aabook_form')



class ABookListView(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'dashboard/book_list.html'
	context_object_name = 'books'
	paginate_by = 3

	def get_queryset(self):
		return Book.objects.order_by('-id')




class AManageBook(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'dashboard/manage_books.html'
	context_object_name = 'books'
	paginate_by = 3

	def get_queryset(self):
		return Book.objects.order_by('-id')

@admin_required
def confirmer_emprunt(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_id, confirme=False)
    emprunt.confirme = True
    emprunt.save()
    messages.success(request, "Emprunt confirmé.")
    return redirect('emprunts_utilisateurs')

@admin_required
def annuler_emprunt(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_id, confirme=False, rendu=False, annule=False)
    
    if request.method == 'GET':
        # Si accès direct par URL sans confirmation
        return redirect('emprunts_utilisateurs')
        
    emprunt.annule = True
    emprunt.livre.disponible = True
    emprunt.save()
    emprunt.livre.save()
    messages.success(request, "Emprunt annulé avec succès.")
    return redirect('emprunts_utilisateurs')

@admin_required
def emprunts_utilisateurs(request):
    emprunts = Emprunt.objects.all().order_by('-date_emprunt')
    return render(request, 'dashboard/feedback.html', {'emprunts': emprunts})


class ADeleteBook(LoginRequiredMixin,DeleteView):
	model = Book
	template_name = 'dashboard/confirm_delete2.html'
	success_url = reverse_lazy('ambook')
	success_message = 'Data was dele successfully'


class ADeleteBookk(LoginRequiredMixin,DeleteView):
	model = Book
	template_name = 'dashboard/confirm_delete.html'
	success_url = reverse_lazy('dashboard')
	success_message = 'Data was dele successfully'


class AViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'dashboard/book_detail.html'



class AEditView(LoginRequiredMixin,UpdateView):
	model = Book
	form_class = BookForm
	template_name = 'dashboard/edit_book.html'
	success_url = reverse_lazy('ambook')
	success_message = 'Data was updated successfully'




class ADeleteRequest(LoginRequiredMixin,ListView):
	model = DeleteRequest
	template_name = 'dashboard/delete_request.html'
	context_object_name = 'feedbacks'
	paginate_by = 3

	def get_queryset(self):
		return DeleteRequest.objects.order_by('-id')



class AFeedback(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'dashboard/feedback.html'
	context_object_name = 'books'
	paginate_by = 3

	def get_queryset(self):
		return Book.objects.order_by('-id')


@admin_required
def asearch(request):
    query = request.GET['query']
    print(type(query))


    #data = query.split()
    data = query
    print(len(data))
    if( len(data) == 0):
        return redirect('dashborad')
    else:
                a = data

                # Searching for It
                qs5 =models.Book.objects.filter(id__iexact=a).distinct()
                qs6 =models.Book.objects.filter(id__exact=a).distinct()

                qs7 =models.Book.objects.all().filter(id__contains=a)
                qs8 =models.Book.objects.select_related().filter(id__contains=a).distinct()
                qs9 =models.Book.objects.filter(id__startswith=a).distinct()
                qs10 =models.Book.objects.filter(id__endswith=a).distinct()
                qs11 =models.Book.objects.filter(id__istartswith=a).distinct()
                qs12 =models.Book.objects.all().filter(id__icontains=a)
                qs13 =models.Book.objects.filter(id__iendswith=a).distinct()




                files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

                res = []
                for i in files:
                    if i not in res:
                        res.append(i)


                # word variable will be shown in html when user click on search button
                word="Aucun resultat trouvé ! :"
                print("Result")

                print(res)
                files = res




                page = request.GET.get('page', 1)
                paginator = Paginator(files, 10)
                try:
                    files = paginator.page(page)
                except PageNotAnInteger:
                    files = paginator.page(1)
                except EmptyPage:
                    files = paginator.page(paginator.num_pages)
   


                if files:
                    return render(request,'dashboard/result.html',{'files':files,'word':word})
                return render(request,'dashboard/result.html',{'files':files,'word':word})
            
            
            
