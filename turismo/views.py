import secrets
import uuid

from django.db.models import Count, Sum
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember,
    Certification, KPI, Faq, Testimonial,
    Category, Package, Reservation,
    ContactMessage, NewsletterSubscriber, PageView
)
from .serializers import (
    SiteInfoSerializer, HeroSlideSerializer, ServiceSerializer,
    AboutBlockSerializer, ValueItemSerializer, TeamMemberSerializer,
    CertificationSerializer, KPISerializer, FaqSerializer,
    TestimonialSerializer, CategorySerializer, PackageSerializer,
    ReservationSerializer, ContactMessageSerializer,
    NewsletterSubscriberSerializer
)

# ======================================================
# BASE: LECTURA PÚBLICA / ESCRITURA ADMIN
# ======================================================
class PublicReadAdminWrite(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]


# ======================================================
# CONFIGURACIÓN DEL SITIO
# ======================================================
class SiteInfoViewSet(PublicReadAdminWrite):
    queryset = SiteInfo.objects.all()
    serializer_class = SiteInfoSerializer


class HeroSlideViewSet(PublicReadAdminWrite):
    queryset = HeroSlide.objects.all()
    serializer_class = HeroSlideSerializer


class ServiceViewSet(PublicReadAdminWrite):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


# ======================================================
# CONTENIDO INSTITUCIONAL
# ======================================================
class AboutBlockViewSet(PublicReadAdminWrite):
    queryset = AboutBlock.objects.all()
    serializer_class = AboutBlockSerializer


class ValueItemViewSet(PublicReadAdminWrite):
    queryset = ValueItem.objects.all()
    serializer_class = ValueItemSerializer


class TeamMemberViewSet(PublicReadAdminWrite):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer


class CertificationViewSet(PublicReadAdminWrite):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class KPIViewSet(PublicReadAdminWrite):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer


class FaqViewSet(PublicReadAdminWrite):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer


class TestimonialViewSet(PublicReadAdminWrite):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer


# ======================================================
# CATÁLOGO DE PAQUETES
# ======================================================
class CategoryViewSet(PublicReadAdminWrite):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PackageViewSet(PublicReadAdminWrite):
    queryset = (
        Package.objects
        .select_related("category")
        .prefetch_related("photos", "includes", "itinerary")
        .all()
    )
    serializer_class = PackageSerializer

    filterset_fields = ["category", "difficulty", "is_popular", "is_featured", "is_active"]
    search_fields = ["title", "short_description", "description", "category__name"]
    ordering_fields = ["price_from", "created_at", "duration_days"]
    ordering = ["-created_at"]


# ======================================================
# RESERVAS
# ======================================================
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("package").all()
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["public_code"] = secrets.token_hex(8)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()

        return Response(
            self.get_serializer(reservation).data,
            status=status.HTTP_201_CREATED
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def my_reservations_lookup(request):
    email = request.query_params.get("email")
    phone = request.query_params.get("phone")

    if not email:
        return Response(
            {"detail": "El correo electrónico es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    qs = Reservation.objects.select_related("package").filter(email__iexact=email)
    if phone:
        qs = qs.filter(phone__icontains=phone)

    return Response(ReservationSerializer(qs, many=True).data)


# ======================================================
# CONTACTO / NEWSLETTER
# ======================================================
class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]


# ======================================================
# TRACKING DE VISITAS
# ======================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def track_pageview(request):
    PageView.objects.create(
        path=request.data.get("path", "/"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
        ip=request.META.get("REMOTE_ADDR")
    )
    return Response({"ok": True})


# ======================================================
# DASHBOARD ADMINISTRATIVO
# ======================================================
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    visits_total = PageView.objects.count()
    reservations_total = Reservation.objects.count()

    ingresos = Reservation.objects.filter(
        status__in=["CONFIRMADO", "CONTACTADO"]
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    tasa_conversion = 0
    if visits_total > 0:
        tasa_conversion = (reservations_total / visits_total) * 100

    reservas_por_estado = (
        Reservation.objects
        .values("status")
        .annotate(total=Count("id"))
        .order_by()
    )

    visitas_mensuales = (
        PageView.objects
        .extra(select={"mes": "MONTH(created_at)"})
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )

    return Response({
        "kpis": {
            "visitas_totales": visits_total,
            "reservas_totales": reservations_total,
            "ingresos": float(ingresos),
            "tasa_conversion": round(tasa_conversion, 2),
        },
        "reservas_por_estado": list(reservas_por_estado),
        "visitas_mensuales": list(visitas_mensuales),
    })
