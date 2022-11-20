from rest_framework.routers import DefaultRouter
import matricula.api.viewsets as mav


router = DefaultRouter()

router.register(r'profesor', mav.TeacherViewSet, basename='profesor')
router.register(r'inscripcion', mav.InscriptionViewSet, basename='inscripcion')
router.register(r'curso', mav.CourseViewSet, basename='curso')
router.register(r'alumno', mav.StudentViewSet, basename='alumno')

urlpatterns = router.urls