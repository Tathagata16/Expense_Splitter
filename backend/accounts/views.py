from django.shortcuts import render
from rest_framework import generics
from .serializers import (RegisterSerializer, LogoutSerializer,CurrentUserSerializer)
from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_205_RESET_CONTENT
        )

class CurrentUserView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        serializer = (
            CurrentUserSerializer(
                request.user
            )
        )

        return Response(
            serializer.data
        )




