from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
        ('employe', 'Employé'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.username} ({self.role})"



class Service(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    categorie = models.CharField(max_length=50)
    duree = models.CharField(max_length=50)
    details = models.JSONField()

    def __str__(self):
        return self.nom
    


from django.utils import timezone

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ]

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'client'},related_name='reservations_as_client')
    employes = models.ManyToManyField(CustomUser, limit_choices_to={'role': 'employe'}, blank=True,related_name='reservations_as_employe')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    annee = models.PositiveIntegerField()
    couleur = models.CharField(max_length=30)
    plaque = models.CharField(max_length=20)
    date_reservation = models.DateField()
    heure_reservation = models.TimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.service.nom} - {self.date_reservation} {self.heure_reservation}"
