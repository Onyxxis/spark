from django.shortcuts import render
from .models import Service

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
# Permission personnalisée : seulement admin peut modifier
from rest_framework.permissions import BasePermission

from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, ServiceSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Auth Token personnalisé avec rôle
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Création d’utilisateur (client / employé / admin)
class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    # permission_classes = [permissions.IsAuthenticated]  
    permission_classes = []  


    def perform_create(self, serializer):
        # Seul un admin peut créer un compte
        # if self.request.user.role != 'admin':
        #     raise PermissionError("Seul un admin peut créer un compte.")
        serializer.save()






class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

# class ServiceViewSet(viewsets.ModelViewSet):
#     queryset = Service.objects.all()
#     serializer_class = ServiceSerializer
#     permission_classes = [IsAuthenticated]

#     def get_permissions(self):
#         if self.action in ['create', 'update', 'partial_update', 'destroy']:
#             return [ IsAuthenticated(),IsAdminUser()]
        
#         return [IsAuthenticated()]

from rest_framework.permissions import AllowAny

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [AllowAny()]
        # IsAuthenticated()
        return []




from .models import Reservation
from .serializers import ReservationWriteSerializer, ReservationReadSerializer

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Reservation, CustomUser
from .serializers import ReservationReadSerializer, ReservationWriteSerializer
from .utils import send_reservation_confirmation_email  # Assure-toi que cette fonction existe

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReservationReadSerializer
        return ReservationWriteSerializer

    def perform_create(self, serializer):
        # Si c'est un client → on utilise le user connecté
        if self.request.user.role == 'client':
            instance = serializer.save(client=self.request.user)
        
        elif self.request.user.role == 'admin':
            client_id = self.request.data.get('client')
            if client_id:
                try:
                    client = CustomUser.objects.get(id=client_id, role='client')
                    instance = serializer.save(client=client)
                except CustomUser.DoesNotExist:
                    raise serializers.ValidationError("Client introuvable ou invalide.")
            else:
                raise serializers.ValidationError("L'admin doit spécifier un client pour la réservation.")
        
        else:
            raise serializers.ValidationError("Seuls les clients ou les admins peuvent créer une réservation.")

        # Envoi de l'email de confirmation
        send_reservation_confirmation_email(
            user_email=instance.client.email,
            service_nom=instance.service.nom,
            date=instance.date_reservation,
            heure=instance.heure_reservation
        )


    def get_queryset(self):
        user = self.request.user

        if user.role == 'client':
            return Reservation.objects.filter(client=user)
        elif user.role == 'employe':
            return Reservation.objects.filter(employes=user)
        else:
            return Reservation.objects.all()




from .utils import send_reservation_confirmation_email


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum
from .models import Reservation, Service, CustomUser

class AdminStatsView(APIView):
    # permission_classes = []
    permission_classes = [AllowAny]  # Permet à tout le monde d'accéder à cette vue

    def get(self, request):
        # 1. Nombre de réservations par service
        reservations_par_service = (
            Reservation.objects.values('service__nom')
            .annotate(nombre=Count('id'))
        )

        # 2. Nombre de services par employé
        reservations_par_employe = (
            CustomUser.objects.filter(role='employe')
            .annotate(nombre=Count('reservation'))
            .values('id', 'email', 'nombre')
        )

        # 3. Points fidélité des clients
        clients_fidelite = (
            CustomUser.objects.filter(role='client')
            .values('id', 'email', 'points_fidelite')
        )

        return Response({
            'reservations_par_service': reservations_par_service,
            'reservations_par_employe': reservations_par_employe,
            'clients_fidelite': clients_fidelite,
        })



User = get_user_model()

class NombreClientsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        nb_clients = User.objects.filter(role='client').count()
        return Response({'nombre_clients': nb_clients})
    
class NombreadminView(APIView):

    def get(self, request):
        nb_admin = User.objects.filter(role='admin').count()
        return Response({'nombre_admin': nb_admin})
    

class NombreEmployeView(APIView):
    def get(self, request):
        nb_employes = User.objects.filter(role='employe').count()
        return Response({'nombre_employes': nb_employes})




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer

class ListeEmployesView(APIView):
    permission_classes = []

    def get(self, request):
        employes = CustomUser.objects.filter(role='employe')
        serializer = UserSerializer(employes, many=True)
        return Response(serializer.data)


class ListeClientView(APIView):
    permission_classes = []

    def get(self, request):
        employes = CustomUser.objects.filter(role='client')
        serializer = UserSerializer(employes, many=True)
        return Response(serializer.data)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []
    lookup_field = 'id'



from django.http import JsonResponse
from .models import Reservation

class NombreReservationView(APIView):
    def get(self, request):
        nombre = Reservation.objects.count()
        return Response({'nombre_reservations': nombre})
    


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Service

class NombreServicesView(APIView):
    def get(self, request):
        nombre = Service.objects.count()
        return Response({'nombre_services': nombre})
    



from .models import Reservation
from decimal import Decimal

class ChiffreAffaireView(APIView):
    def get(self, request):
        reservations = Reservation.objects.select_related('service').all()
        total = sum([res.service.prix for res in reservations if res.service and res.service.prix], Decimal('0.00'))
        return Response({'chiffre_affaire': float(total)})




from .models import Reservation, CustomUser
from .serializers import ReservationReadSerializer, UserSerializer

class ActivitesRecentesView(APIView):
    def get(self, request):
        dernier_client = CustomUser.objects.filter(role='client').order_by('-date_joined').first()
        derniere_reservation = Reservation.objects.select_related('client', 'service').order_by('-created_at').first()
        derniere_reservation_terminee = Reservation.objects.select_related('client', 'service').filter(statut='terminee').order_by('-created_at').first()

        return Response({
            'dernier_client': UserSerializer(dernier_client).data if dernier_client else None,
            'derniere_reservation': ReservationReadSerializer(derniere_reservation).data if derniere_reservation else None,
            'derniere_reservation_terminee': ReservationReadSerializer(derniere_reservation_terminee).data if derniere_reservation_terminee else None,
        })



from .models import Reservation
from .serializers import ReservationReadSerializer

class ReservationCalendarAPIView(APIView):
    def get(self, request):
        reservations = Reservation.objects.all()
        events = []

        for r in reservations:
            couleur = '#dc3545'  # rouge par défaut
            if r.employes.exists():
                if r.statut == 'en_attente':
                    couleur = '#ffc107'  # jaune
                elif r.statut == 'en_cours':
                    couleur = '#0d6efd'  # bleu
                elif r.statut == 'terminee':
                    couleur = '#198754'  # vert

            events.append({
                "id": r.id,
                "title": f"{r.service.nom} — {r.heure_reservation.strftime('%H:%M')}",
                "start": f"{r.date_reservation}T{r.heure_reservation}",
                "color": couleur
            })

        return Response(events)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Reservation
from .serializers import ReservationReadSerializer

class ReservationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Récupérer l'utilisateur connecté
        user = request.user

        # Filtrer les réservations de cet utilisateur, en utilisant l'ID de l'utilisateur connecté
        reservations = Reservation.objects.filter(client=user)  # Supposons que 'client' est une clé étrangère vers l'utilisateur

        # Sérialiser les données des réservations
        serializer = ReservationReadSerializer(reservations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
