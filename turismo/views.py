import secrets
import uuid

from django.db.models import Count, Sum
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember,
    Certification, KPI, Faq, Testimonial,
    Category, Package, Reservation,
    ContactMessage, NewsletterSubscriber, PageView,
    PackagePhoto, Cart, CartItem, Payment
)

from .serializers import (
    SiteInfoSerializer, HeroSlideSerializer, ServiceSerializer,
    AboutBlockSerializer, ValueItemSerializer, TeamMemberSerializer,
    CertificationSerializer, KPISerializer, FaqSerializer,
    TestimonialSerializer, CategorySerializer, PackageSerializer,
    ReservationSerializer, ContactMessageSerializer,
    NewsletterSubscriberSerializer, PackagePhotoSerializer,
    CartSerializer, CartItemSerializer, PaymentSerializer
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

    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def add_photos(self, request, pk=None):
        package = self.get_object()

        files = request.FILES.getlist("photos")
        if not files:
            return Response(
                {"detail": "Envía 1 o más archivos en el campo 'photos' (form-data)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        start_order = int(request.data.get("start_order", 0))

        for i, f in enumerate(files):
            created.append(
                PackagePhoto.objects.create(
                    package=package,
                    image=f,
                    order=start_order + i
                )
            )

        serializer = PackagePhotoSerializer(created, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


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

    return Response(ReservationSerializer(qs, many=True, context={"request": request}).data)


# ======================================================
# CARRITO / PAGO SIMULADO
# ======================================================
class CartViewSet(viewsets.ModelViewSet):
    queryset = (
        Cart.objects
        .prefetch_related("items__package", "items__reservation")
        .all()
    )
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def _expire_if_needed(self, cart):
        if cart.status == "ABIERTO" and cart.expires_at and timezone.now() > cart.expires_at:
            cart.status = "EXPIRADO"
            cart.save(update_fields=["status", "updated_at"])
            Reservation.objects.filter(cart_item__cart=cart, status="PENDIENTE").update(status="CANCELADO")
            return True
        return False

    @action(detail=False, methods=["get"])
    def by_email(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "email es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        cart = (
            Cart.objects
            .prefetch_related("items__package", "items__reservation")
            .filter(email__iexact=email)
            .order_by("-created_at")
            .first()
        )
        if not cart:
            return Response({"detail": "No existe carrito para ese email"}, status=status.HTTP_404_NOT_FOUND)

        self._expire_if_needed(cart)
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def add_item(self, request, pk=None):
        cart = self.get_object()

        if cart.status != "ABIERTO":
            return Response({"detail": "El carrito no está ABIERTO"}, status=status.HTTP_400_BAD_REQUEST)

        if self._expire_if_needed(cart):
            return Response({"detail": "El carrito está EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)

        package_id = request.data.get("package_id")
        full_name = request.data.get("full_name")
        email = request.data.get("email") or cart.email
        phone = request.data.get("phone") or cart.phone
        nationality = request.data.get("nationality") or cart.nationality

        travel_date = request.data.get("travel_date")
        adults = int(request.data.get("adults", 1))
        children = int(request.data.get("children", 0))
        notes = request.data.get("notes")

        if not package_id:
            return Response({"detail": "package_id es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
        if not full_name:
            return Response({"detail": "full_name es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({"detail": "Paquete no existe"}, status=status.HTTP_404_NOT_FOUND)

        reservation = Reservation.objects.create(
            package=package,
            full_name=full_name,
            email=email,
            phone=phone,
            travel_date=travel_date,
            adults=adults,
            children=children,
            nationality=nationality,
            notes=notes,
            status="PENDIENTE",
            total_amount=None,
            currency=package.currency,
            public_code=secrets.token_hex(8),
        )

        item = CartItem.objects.create(
            cart=cart,
            package=package,
            reservation=reservation,
            travel_date=travel_date,
            adults=adults,
            children=children,
            unit_price=package.price_from,
            currency=package.currency,
        )

        return Response(CartItemSerializer(item, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def remove_item(self, request, pk=None):
        cart = self.get_object()

        if cart.status != "ABIERTO":
            return Response({"detail": "El carrito no está ABIERTO"}, status=status.HTTP_400_BAD_REQUEST)

        if self._expire_if_needed(cart):
            return Response({"detail": "El carrito está EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)

        item_id = request.data.get("item_id")
        if not item_id:
            return Response({"detail": "item_id es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.select_related("reservation").get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item no existe en este carrito"}, status=status.HTTP_404_NOT_FOUND)

        if item.reservation and item.reservation.status == "PENDIENTE":
            item.reservation.status = "CANCELADO"
            item.reservation.save(update_fields=["status", "updated_at"])

        item.delete()
        return Response({"ok": True})

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def simulate_payment(self, request, pk=None):
        cart = self.get_object()

        if cart.status != "ABIERTO":
            return Response({"detail": "El carrito no está ABIERTO"}, status=status.HTTP_400_BAD_REQUEST)

        if self._expire_if_needed(cart):
            return Response({"detail": "El carrito está EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)

        items = cart.items.select_related("reservation").all()
        if not items.exists():
            return Response({"detail": "El carrito no tiene items"}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(i.line_total() for i in items)

        payment = Payment.objects.create(
            cart=cart,
            amount=total,
            currency=items.first().currency if items.first() else "USD",
            provider="SIMULADO",
            status="APROBADO",
            reference=str(uuid.uuid4()),
        )

        cart.status = "PAGADO"
        cart.save(update_fields=["status", "updated_at"])

        for i in items:
            if i.reservation and i.reservation.status == "PENDIENTE":
                i.reservation.status = "CONFIRMADO"
                i.reservation.total_amount = i.line_total()
                i.reservation.currency = i.currency
                i.reservation.save(update_fields=["status", "total_amount", "currency", "updated_at"])

        return Response({
            "cart_id": cart.id,
            "cart_status": cart.status,
            "payment_reference": payment.reference,
            "amount": float(total),
            "currency": payment.currency,
        })


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
import secrets
import uuid

from django.db.models import Count, Sum
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember,
    Certification, KPI, Faq, Testimonial,
    Category, Package, Reservation,
    ContactMessage, NewsletterSubscriber, PageView,
    PackagePhoto, Cart, CartItem, Payment
)

from .serializers import (
    SiteInfoSerializer, HeroSlideSerializer, ServiceSerializer,
    AboutBlockSerializer, ValueItemSerializer, TeamMemberSerializer,
    CertificationSerializer, KPISerializer, FaqSerializer,
    TestimonialSerializer, CategorySerializer, PackageSerializer,
    ReservationSerializer, ContactMessageSerializer,
    NewsletterSubscriberSerializer, PackagePhotoSerializer,
    CartSerializer, CartItemSerializer, PaymentSerializer
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

    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def add_photos(self, request, pk=None):
        package = self.get_object()

        files = request.FILES.getlist("photos")
        if not files:
            return Response(
                {"detail": "Envía 1 o más archivos en el campo 'photos' (form-data)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        start_order = int(request.data.get("start_order", 0))

        for i, f in enumerate(files):
            created.append(
                PackagePhoto.objects.create(
                    package=package,
                    image=f,
                    order=start_order + i
                )
            )

        serializer = PackagePhotoSerializer(created, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


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

    return Response(ReservationSerializer(qs, many=True, context={"request": request}).data)


# ======================================================
# CARRITO / PAGO SIMULADO
# ======================================================
class CartViewSet(viewsets.ModelViewSet):
    queryset = (
        Cart.objects
        .prefetch_related("items__package", "items__reservation")
        .all()
    )
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def _expire_if_needed(self, cart):
        if cart.status == "ABIERTO" and cart.expires_at and timezone.now() > cart.expires_at:
            cart.status = "EXPIRADO"
            cart.save(update_fields=["status", "updated_at"])
            Reservation.objects.filter(cart_item__cart=cart, status="PENDIENTE").update(status="CANCELADO")
            return True
        return False

    @action(detail=False, methods=["get"])
    def by_email(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "email es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        cart = (
            Cart.objects
            .prefetch_related("items__package", "items__reservation")
            .filter(email__iexact=email)
            .order_by("-created_at")
            .first()
        )
        if not cart:
            return Response({"detail": "No existe carrito para ese email"}, status=status.HTTP_404_NOT_FOUND)

        self._expire_if_needed(cart)
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def add_item(self, request, pk=None):
        cart = self.get_object()

        if cart.status != "ABIERTO":
            return Response({"detail": "El carrito no está ABIERTO"}, status=status.HTTP_400_BAD_REQUEST)

        if self._expire_if_needed(cart):
            return Response({"detail": "El carrito está EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)

        package_id = request.data.get("package_id")
        full_name = request.data.get("full_name")
        email = request.data.get("email") or cart.email
        phone = request.data.get("phone") or cart.phone
        nationality = request.data.get("nationality") or cart.nationality

        travel_date = request.data.get("travel_date")
        adults = int(request.data.get("adults", 1))
        children = int(request.data.get("children", 0))
        notes = request.data.get("notes")

        if not package_id:
            return Response({"detail": "package_id es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
        if not full_name:
            return Response({"detail": "full_name es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({"detail": "Paquete no existe"}, status=status.HTTP_404_NOT_FOUND)

        reservation = Reservation.objects.create(
            package=package,
            full_name=full_name,
            email=email,
            phone=phone,
            travel_date=travel_date,
            adults=adults,
            children=children,
            nationality=nationality,
            notes=notes,
            status="PENDIENTE",
            total_amount=None,
            currency=package.currency,
            public_code=secrets.token_hex(8),
        )

        item = CartItem.objects.create(
            cart=cart,
            package=package,
            reservation=reservation,
            travel_date=travel_date,
            adults=adults,
            children=children,
            unit_price=package.price_from,
            currency=package.currency,
        )

        return Response(CartItemSerializer(item, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def remove_item(self, request, pk=None):
        cart = self.get_object()

        if cart.status != "ABIERTO":
            return Response({"detail": "El carrito no está ABIERTO"}, status=status.HTTP_400_BAD_REQUEST)

        if self._expire_if_needed(cart):
            return Response({"detail": "El carrito está EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)

        item_id = request.data.get("item_id")
        if not item_id:
            return Response({"detail": "item_id es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.select_related("reservation").get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item no existe en este carrito"}, status=status.HTTP_404_NOT_FOUND)

        if item.reservation and item.reservation.status == "PENDIENTE":
            item.reservation.status = "CANCELADO"
            item.reservation.save(update_fields=["status", "updated_at"])

        item.delete()
        return Response({"ok": True})

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def simulate_payment(self, request, pk=None):
        cart = self.get_object()

        if cart.status != "ABIERTO":
            return Response({"detail": "El carrito no está ABIERTO"}, status=status.HTTP_400_BAD_REQUEST)

        if self._expire_if_needed(cart):
            return Response({"detail": "El carrito está EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)

        items = cart.items.select_related("reservation").all()
        if not items.exists():
            return Response({"detail": "El carrito no tiene items"}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(i.line_total() for i in items)

        payment = Payment.objects.create(
            cart=cart,
            amount=total,
            currency=items.first().currency if items.first() else "USD",
            provider="SIMULADO",
            status="APROBADO",
            reference=str(uuid.uuid4()),
        )

        cart.status = "PAGADO"
        cart.save(update_fields=["status", "updated_at"])

        for i in items:
            if i.reservation and i.reservation.status == "PENDIENTE":
                i.reservation.status = "CONFIRMADO"
                i.reservation.total_amount = i.line_total()
                i.reservation.currency = i.currency
                i.reservation.save(update_fields=["status", "total_amount", "currency", "updated_at"])

        return Response({
            "cart_id": cart.id,
            "cart_status": cart.status,
            "payment_reference": payment.reference,
            "amount": float(total),
            "currency": payment.currency,
        })


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
