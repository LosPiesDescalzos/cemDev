import datetime
from datetime import date, timedelta
from django.shortcuts import render
from .models import Client, Team, Trainer, Activity, News, Area, SportType, Abonement
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
import json
from django.db.models import Q
from django.utils import timezone
from django.db.models import Count


def login_page(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main'))
    else:
        return render(request, 'trainers/login.html')


def log_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('login_page'))
    else:
        return HttpResponseRedirect(reverse('main'))


def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('login_page'))


def main(request):
    if request.user.is_authenticated:
        news = News.objects.filter(pub_date__lte=timezone.now(), expiry_date__gt=timezone.now())
        areas = Area.objects.all()
        sport_types = SportType.objects.all()
        abonements = Abonement.objects.all()

        if request.user.trainer.status == "Директор":
            context = {'userinfo': request.user,
                       'trainer': request.user.trainer,
                       'news': news,
                       'areas': areas,
                       'sport_types': sport_types,
                       'abonements': abonements}

        return render(request, 'trainers/main.html', context)
    else:
        return HttpResponseRedirect(reverse('login_page'))


def clients(request):
    if request.user.is_authenticated:
        clients = Client.objects.all()
        teams = Team.objects.all()
        trainers = Trainer.objects.filter(status="Тренер")
        sport_types = SportType.objects.all()
        areas = Area.objects.all()

        context = {'clients': clients,
                   'teams': teams,
                   'trainers':trainers,
                   'sport_types':sport_types,
                   'areas':areas}

        return render(request, "trainers/clients.html", context)
    else:
        return HttpResponseRedirect(reverse('login_page'))


def client_info(request, client_id):
    if request.user.is_authenticated:
        client = get_object_or_404(Client, pk=client_id)
        adr = client.address_set.all()
        context = {'client': client,
                   'adr': adr}
        return render(request, "trainers/clients_info.html", context)
    else:
        return HttpResponseRedirect(reverse('login_page'))


def client_add_action(request):
    client_name = request.POST['client_name']
    client_surname = request.POST['client_surname']
    client_birthdate = request.POST['client_birthdate']
    try:
        Client.objects.create(first_name=client_name, last_name=client_surname, birth_date=client_birthdate)
        return HttpResponseRedirect(reverse('clients'))
    except:
        return HttpResponseRedirect(reverse('client_add'))


def team_creation(request):
    team_name = request.POST.get('title')
    sport_type = request.POST['sport_type']
    members = request.POST.getlist('members')
    trainer = request.POST['trainer']
    date_end = request.POST['date_end']
    area = request.POST['area']
    #___________________Нужно изменить
    days = request.POST.getlist('days')
    act_begin_time = request.POST['act_begin_time']
    act_end_time = request.POST['act_end_time']
    #__________________________________

    tr = get_object_or_404(Trainer, pk=trainer)
    sp_type = get_object_or_404(SportType, pk=sport_type)
    area = get_object_or_404(Area, pk=area)
    team = Team.objects.create(name=team_name, trainer=tr, sport_type=sp_type)
    for client in members:
        team.clients.add(client)

    date1 = datetime.date.today()
    date2 = datetime.datetime.strptime(date_end, '%Y-%m-%d')

    while date1 <= date2.date():
        if str(date1.weekday()) in days:
            act = Activity(act_date=date1, act_time_begin=act_begin_time,
                            act_time_end=act_end_time, trainer=tr, area=area)
            act.save()
            for client in members:
                act.clients.add(client)
            act.save()
        date1 = date1 + datetime.timedelta(days=1)

    return HttpResponseRedirect(reverse('clients'))


def trainers(request):
    if request.user.is_authenticated:
        trainers = Trainer.objects.filter(status__in=['Тренер', 'Менеджер'])

        today = date.today()
        trainers_birth = Trainer.objects.order_by('birthdate')
        upcoming_birthdays = []
        today_birthdays = []
        for trainer in trainers_birth:
            # дата> рождения тренера в этом году
            birthdate_this_year = date(today.year, trainer.birthdate.month, trainer.birthdate.day)
            if birthdate_this_year < today:
                birthdate_this_year = date(today.year + 1, trainer.birthdate.month, trainer.birthdate.day)
            # оставшееся время до дня рождения
            time_to_birthday = (birthdate_this_year - today).days
            if time_to_birthday <= 7 & time_to_birthday != 0:
                upcoming_birthdays.append(trainer)
            if time_to_birthday == 0:
                today_birthdays.append(trainer)
        trainers_search = []
        query = request.GET.get('q')
        if query:
            trainers_search = Trainer.objects.filter(
                Q(user__first_name__icontains=query) | Q(user__email__icontains=query))

        context = {'trainers': trainers,
                   'upcoming_birthdays': upcoming_birthdays,
                   'today_birthdays': today_birthdays,
                   'trainers_search': trainers_search,
                   'query': query,
                   'user': request.user}


        return render(request, "trainers/trainers.html", context)
    else:
        return HttpResponseRedirect(reverse('login_page'))


def trainers_add_action(request):
    trainer_name = request.POST['name']
    trainer_last_name = request.POST['last_name']
    trainer_otchestv = request.POST['otchestv']
    trainer_mail = request.POST['mail']
    trainer_pass = request.POST['password']
    trainer_birthdate = request.POST['birth_date']
    status = request.POST['status']
    try:
        user = User.objects.create_user(username=trainer_mail, email=trainer_mail, password=trainer_pass)
        user.last_name = trainer_last_name
        user.first_name = trainer_name
        user.save()
        trainer = Trainer(user=user, otchestv=trainer_otchestv, birthdate=trainer_birthdate, status=status)
        trainer.save()
        return HttpResponseRedirect(reverse('trainers'))
    except:
        return HttpResponseRedirect(reverse('trainers'))


def schedule(request):
    if request.user.is_authenticated:
        activities = Activity.objects.all()
        context = {'activities': activities}
        return render(request, "trainers/schedule.html", context)
    else:
        return HttpResponseRedirect(reverse('login_page'))


def sport_type_creation(request):
    title = request.POST['title']
    sport_type = SportType(title=title)
    sport_type.save()
    return HttpResponseRedirect(reverse('main'))


def area_creation(request):
    adres = request.POST['adres']
    area = Area(adres=adres)
    area.save()
    return HttpResponseRedirect(reverse('main'))


def abonement_creation(request):
    title = request.POST['title']
    price = request.POST['price']
    is_duration = request.POST.get('duration_check', False)
    is_count = request.POST.get('count_check', False)

    if is_count == 'on':
        count = request.POST['count']
    else:
        count = None

    if is_duration == 'on':
        duration = request.POST['duration']
        duration_type = request.POST['duration_type']
        if duration_type == 'days':
            dur = timedelta(days=int(duration))
        elif duration_type == 'weeks':
            dur = timedelta(weeks=int(duration))
        elif duration_type == 'month':
            dur = timedelta(days=int(duration)*30)
    else:
        dur=None

    abonement = Abonement.objects.create(title=title, price=price, lesson_count=count, duration=dur)
    abonement.save()

    return HttpResponseRedirect(reverse('main'))
