import secrets
from django.db.models import Count, Sum
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember, Certification, KPI,
    Faq, Testimonial, Category, Package, Reservation, ContactMessage, NewsletterSubscriber,
    PageView
)
from .serializers import (
    SiteInfoSerializer, HeroSlideSerializer, ServiceSerializer, AboutBlockSerializer,
    ValueItemSerializer, TeamMemberSerializer, CertificationSerializer, KPISerializer,
    FaqSerializer, TestimonialSerializer, CategorySerializer, PackageSerializer,
    ReservationSerializer, ContactMessageSerializer, NewsletterSubscriberSerializer
)

class PublicReadAdminWrite(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    def get_permissions(self):
        if self.request.method in ("POST","PUT","PATCH","DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]

class SiteInfoViewSet(PublicReadAdminWrite):
    queryset = SiteInfo.objects.all()
    serializer_class = SiteInfoSerializer

class HeroSlideViewSet(PublicReadAdminWrite):
    queryset = HeroSlide.objects.all()
    serializer_class = HeroSlideSerializer

class ServiceViewSet(PublicReadAdminWrite):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

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

class CategoryViewSet(PublicReadAdminWrite):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PackageViewSet(PublicReadAdminWrite):
    queryset = Package.objects.select_related("category").prefetch_related("photos","includes","itinerary").all()
    serializer_class = PackageSerializer

    filterset_fields = ["category", "difficulty", "is_popular", "is_featured", "is_active"]
    search_fields = ["title", "short_description", "description", "category__name"]
    ordering_fields = ["price_from", "created_at", "duration_days"]
    ordering = ["-created_at"]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("package").all()
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.action in ("list","retrieve","update","partial_update","destroy"):
            return [IsAdminUser()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["public_code"] = secrets.token_hex(8)  # 16 chars
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([AllowAny])
def my_reservations_lookup(request):
    email = request.query_params.get("email")
    phone = request.query_params.get("phone")
    if not email:
        return Response({"detail": "email es requerido"}, status=400)

    qs = Reservation.objects.select_related("package").filter(email__iexact=email)
    if phone:
        qs = qs.filter(phone__icontains=phone)

    return Response(ReservationSerializer(qs, many=True).data)

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.request.method in ("GET","PUT","PATCH","DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]

class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer

    def get_permissions(self):
        if self.request.method in ("GET","PUT","PATCH","DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]

@api_view(["POST"])
@permission_classes([AllowAny])
def track_pageview(request):
    path = request.data.get("path", "/")
    ua = request.META.get("HTTP_USER_AGENT")
    ip = request.META.get("REMOTE_ADDR")
    PageView.objects.create(path=path, user_agent=ua[:255] if ua else None, ip=ip)
    return Response({"ok": True})

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    now = timezone.now()
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    visits_total = PageView.objects.count()
    reservations_total = Reservation.objects.count()
    ingresos = Reservation.objects.filter(status__in=["CONFIRMADO","CONTACTADO"]).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    conv = 0
    if visits_total > 0:
        conv = (reservations_total / visits_total) * 100

    reservations_by_status = (
        Reservation.objects.values("status").annotate(count=Count("id")).order_by()
    )

    monthly = (
        PageView.objects.filter(created_at__gte=start_month)
        .extra(select={"m": "MONTH(created_at)"})
        .values("m")
        .annotate(visitas=Count("id"))
        .order_by("m")
    )

    return Response({
        "kpis": {
            "visitas_totales": visits_total,
            "reservas_totales": reservations_total,
            "ingresos": float(ingresos) if ingresos else 0,
            "tasa_conversion": round(conv, 2),
        },
        "visitas_mensuales": list(monthly),
        "reservas_por_estado": list(reservations_by_status),
    })
