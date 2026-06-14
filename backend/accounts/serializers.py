from rest_framework import serializers
from .models import User

from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class LogoutSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def save(self):
        refresh_token = self.validated_data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()

from rest_framework import serializers

from .models import User


class CurrentUserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
        ]

