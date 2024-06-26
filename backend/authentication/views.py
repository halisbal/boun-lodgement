import logging

from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .models import User
from .permissions import IsAuthenticatedAdmin
from .serializers import UserSerializer, UserUpdateSerializer
from constants import ALLOWED_EMAILS, UserRoles


class AuthView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or email not in ALLOWED_EMAILS:
            return Response({"error": "Invalid or not allowed email"}, status=400)

        try:
            user, created = User.objects.get_or_create(
                email=email, defaults={"role": UserRoles.USER.value}, username=email
            )
            if created:
                user.set_password(password)
                user.save()
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        print(f"User: {user.id}, Type: {type(user)}")

        if user is None or not isinstance(user, User):
            return Response({"error": "User creation failed"}, status=500)

        try:
            token, created = Token.objects.get_or_create(user=user)
        except Exception as e:
            logging.error(f"Error in token creation: {e}")
            return Response({"error": "Token creation failed"}, status=500)
        return Response({"token": token.key})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedAdmin]

    def get_serializer_class(self):
        if self.action == "edit":
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=True, methods=["patch"], url_path="edit", url_name="edit")
    def edit(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
