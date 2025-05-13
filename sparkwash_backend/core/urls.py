from django.urls import include, path
from .views import ActivitesRecentesView, AdminStatsView, ChiffreAffaireView, ListeClientView, ListeEmployesView, MyTokenObtainPairView, NombreEmployeView, NombreReservationView, NombreServicesView, NombreadminView, RegisterUserView, ReservationCalendarAPIView, ReservationHistoryView, ServiceViewSet, ReservationViewSet,NombreClientsView, UserDetailView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from rest_framework import routers

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'reservations', ReservationViewSet, basename='reservation')



urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterUserView.as_view(), name='register_user'),
    path('admin/statistiques/', AdminStatsView.as_view(), name='admin-stats'),
    path('nombre-clients/', NombreClientsView.as_view(), name='nombre_clients'),
    path('nombre-admin/', NombreadminView.as_view(), name='nombre_admin'),
    path('nombre-employes/', NombreEmployeView.as_view(), name='nombre_employes'),
    path('liste-employes/', ListeEmployesView.as_view(), name='liste_employes'),
    path('liste-client/', ListeClientView.as_view(), name='liste_client'),
    path('utilisateurs/<int:id>/', UserDetailView.as_view(), name='user_detail'),
    path('reservations/count/', NombreReservationView.as_view(), name='nombre_reservations'),
    path('reservations/chiffre-affaire/', ChiffreAffaireView.as_view(), name='chiffre_affaire'),
    path('services/count/', NombreServicesView.as_view(), name='nombre_services'),
    path('activites-recentes/', ActivitesRecentesView.as_view(), name='activites_recentes'),
    path('reservation-history/', ReservationHistoryView.as_view(), name='reservation-history'),


    path('calendar/reservations/', ReservationCalendarAPIView.as_view(), name='calendar-reservations'),










]

urlpatterns += router.urls
