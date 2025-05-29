from django.shortcuts import redirect


class ForcePasswordChangeMiddleware:
    """
    Middleware to force password change on first login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifie si l'utilisateur est authentifié
        if request.user.is_authenticated:
            # Vérifie si l'utilisateur doit changer son mot de passe
            if request.user.doit_changer_mot_de_passe:
                # Empêche les boucles en autorisant certaines URLs

                allowed_paths = [
                    redirect('accounts:change_password').url,
                    redirect('accounts:logout').url,
                ]

                # Vérifie si la requête n'est pas pour changer le mot de passe ou se déconnecter
                if request.path not in allowed_paths:
                    # Redirige vers la page de changement de mot de passe
                    return redirect('accounts:change_password')
                
        return self.get_response(request)
                