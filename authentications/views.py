from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import CreateUserSerializer, OrganisationSerializer, UserLoginSerializer, UserSerializer, AddUserToOrganisationSerializer
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import make_password



@extend_schema(
    request=CreateUserSerializer,
    tags=["Auth"],
)
class RegisterView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

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
            "statusCode": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
    lookup_field = 'userId'

    def get(self, request, *args, **kwargs):

        user = self.get_object() 
        serializer = self.get_serializer(user)

        return Response({
            "status": "success",
            "message": "User details retrieved",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": "success",
            "message": "Your organisations details retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class OrganisationDetailView(generics.RetrieveAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'orgId'

    def get_queryset(self):
        return self.request.user.organisations.all()

    def retrieve(self, request, *args, **kwargs):
        org = self.get_object()

        response_data = {
            "status": "success",
            "message": "Organisation details retrieved successfully",
            "data": {
                "organisation": {
                    "orgId": org.orgId,
                    "name": org.name,
                    "description": org.description,
                }
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    request=OrganisationSerializer,
    tags=["Organization"],
)
class OrganisationCreateView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = {
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "orgId": serializer.data.get('orgId'),
                "name": serializer.data.get('name'),
                "description": serializer.data.get('description')
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    request=AddUserToOrganisationSerializer,
    tags=["Organization"],
)
class AddUserToOrganisationView(generics.GenericAPIView):
    serializer_class = AddUserToOrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['userId']

        try:
            organisation = Organisation.objects.get(orgId=orgId)
            user = User.objects.get(userId=user_id)

            organisation.users.add(user)
            return Response({
                "status": "success",
                "message": "User added to organisation successfully",
            }, status=status.HTTP_200_OK)

        except Organisation.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Organisation not found",
            }, status=status.HTTP_404_NOT_FOUND)
        
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found",
            }, status=status.HTTP_404_NOT_FOUND)
