from django.urls import path
from rest_framework_extensions.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from billing import views

app_name = 'billing'

router = DefaultRouter(trailing_slash=False)
router.register(r'users', views.UserViewSet)
router.register(r'bills', views.BillViewSet)
router.register(
    r'transactions/in',
    views.TransactionInViewSet,
    basename='transactions/in'
)
router.register(
    r'transactions/out',
    views.TransactionOutViewSet,
    basename='transactions/out'
)

urlpatterns = [
    path(
        'users/login',
        jwt_views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'users/refresh-token',
        jwt_views.TokenRefreshView.as_view(),
        name='token_refresh'
    ),
] + router.urls
