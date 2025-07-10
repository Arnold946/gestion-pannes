from pannes.models import Notification

def notifications_utilisateur(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_envoi')[:3]
        non_lues = Notification.objects.filter(utilisateur=request.user, est_lue=False).count()
    else:
        notifications = []
        non_lues = 0

    return {
        'notifications_utilisateur': notifications,
        'nb_notifications_non_lues': non_lues,
    }
