from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer, UserLoginSerializer
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import make_password



@extend_schema(
    request=UserSerializer,
    tags=["Auth"],
)
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(password=make_password(serializer.validated_data['password']))
            # Create a default organisation for the user
            organisation_name = f"{user.first_name}'s Organisation"
            organisation = Organisation.objects.create(name=organisation_name, description='')
            organisation.users.add(user)
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": access_token,
                    "user": {
                        "userId": user.userId,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 422,
            "errors": serializer.errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

@extend_schema(
    request=UserLoginSerializer,
    tags=["Auth"],
)
class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": access_token,
                    "user": {
                        "userId": user.userId,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    request=UserSerializer,
    tags=["Auth"],
)
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user

@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class OrganisationCreateView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])

@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class AddUserToOrganisationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId, *args, **kwargs):
        try:
            organisation = Organisation.objects.get(orgId=orgId, users=request.user)
            user_id = request.data.get('userId')
            user = User.objects.get(userId=user_id)
            organisation.users.add(user)
            return Response({
                "status": "success",
                "message": "User added to organisation successfully",
            }, status=status.HTTP_200_OK)
        except Organisation.DoesNotExist:
            return Response({
                "status": "Bad Request",
                "message": "Organisation not found or you don't have access",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "status": "Bad Request",
                "message": "User not found",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({
                "status": "Bad Request",
                "message": "User already belongs to the organisation",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
