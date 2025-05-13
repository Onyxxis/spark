from rest_framework import serializers
from .models import CustomUser
from .models import Service
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')
    
    def create(self, validated_data):
        # Création d'un utilisateur avec mot de passe
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user
    
    def update(self, instance, validated_data):
        # Si un mot de passe est fourni, le mettre à jour
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # Modifier le mot de passe
        # Mettre à jour les autres champs
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


from .models import Reservation


class ReservationReadSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    employes = UserSerializer(many=True, read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'

class ReservationWriteSerializer(serializers.ModelSerializer):
    employes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.filter(role='employe'),
        required=False
    )
    client = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='client'), required=False)
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['created_at']


# class ReservationSerializer(serializers.ModelSerializer):
#     employes = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=CustomUser.objects.filter(role='employe'),
#         required=False
#     )
#     client = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='client'), required=False)

#     class Meta:
#         model = Reservation
#         fields = '__all__'
#         read_only_fields = ['client', 'statut', 'created_at']