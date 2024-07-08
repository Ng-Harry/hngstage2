from django.urls import path
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", SpectacularSwaggerView.as_view(url_name="schema")),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('api/users/<uuid:userId>/', views.UserDetailView.as_view(), name='user_detail'),
    path('api/organisations/', views.OrganisationListView.as_view(), name='organisation_list'),
    path('api/organisations/<uuid:orgId>/', views.OrganisationDetailView.as_view(), name='organisation_detail'),
    path('api/organisations/create/', views.OrganisationCreateView.as_view(), name='organisation_create'),
    path('api/organisations/<uuid:orgId>/users/', views.AddUserToOrganisationView.as_view(), name='add_user_to_organisation'),
]
