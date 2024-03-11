from rest_framework.routers import DefaultRouter
import users.api.viewsets as usv


router = DefaultRouter(trailing_slash=False)

router.register(r'usuarios', usv.UserViewSet, basename='usuario')

urlpatterns = router.urls
