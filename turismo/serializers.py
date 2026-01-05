from rest_framework import serializers
from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember,
    Certification, KPI, Faq, Testimonial,
    Category, Package, PackagePhoto, PackageInclude, PackageItinerary,
    Reservation, ContactMessage, NewsletterSubscriber, PageView,
    Cart, CartItem, Payment
)

# ======================================================
# CONFIGURACIÓN DEL SITIO
# ======================================================
class SiteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = "__all__"


class HeroSlideSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HeroSlide
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


# ======================================================
# CONTENIDO INSTITUCIONAL
# ======================================================
class AboutBlockSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutBlock
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None


class ValueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueItem
        fields = "__all__"


class TeamMemberSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = "__all__"

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        if obj.avatar:
            return obj.avatar.url
        return None


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"


class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = "__all__"


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = "__all__"


# ======================================================
# CATÁLOGO
# ======================================================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PackagePhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PackagePhoto
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None


class PackageIncludeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageInclude
        fields = "__all__"


class PackageItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageItinerary
        fields = "__all__"


class PackageSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True
    )

    cover_url = serializers.SerializerMethodField()
    photos = PackagePhotoSerializer(many=True, read_only=True)
    includes = PackageIncludeSerializer(many=True, read_only=True)
    itinerary = PackageItinerarySerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = "__all__"

    def get_cover_url(self, obj):
        request = self.context.get("request")
        if obj.cover and request:
            return request.build_absolute_uri(obj.cover.url)
        if obj.cover:
            return obj.cover.url
        return None


# ======================================================
# RESERVAS
# ======================================================
class ReservationSerializer(serializers.ModelSerializer):
    package = PackageSerializer(read_only=True)
    package_id = serializers.PrimaryKeyRelatedField(
        source="package",
        queryset=Package.objects.all(),
        write_only=True
    )

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = (
            "public_code",
            "created_at",
            "updated_at",
        )


# ======================================================
# CARRITO / ITEMS / PAGO (SIMULADO)
# ======================================================
class CartItemSerializer(serializers.ModelSerializer):
    package = PackageSerializer(read_only=True)
    package_id = serializers.PrimaryKeyRelatedField(
        source="package",
        queryset=Package.objects.all(),
        write_only=True
    )

    reservation = ReservationSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = "__all__"

    def get_line_total(self, obj):
        try:
            return float(obj.line_total())
        except Exception:
            return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


# ======================================================
# CONTACTO / NEWSLETTER / TRACKING
# ======================================================
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = "__all__"


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = "__all__"
