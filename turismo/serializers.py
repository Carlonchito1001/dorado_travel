from rest_framework import serializers
from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember,
    Certification, KPI, Faq, Testimonial,
    Category, Package, PackagePhoto, PackageInclude, PackageItinerary,
    Reservation, ContactMessage, NewsletterSubscriber, PageView
)

# ======================================================
# CONFIGURACIÓN DEL SITIO
# ======================================================
class SiteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = "__all__"


class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


# ======================================================
# CONTENIDO INSTITUCIONAL
# ======================================================
class AboutBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutBlock
        fields = "__all__"


class ValueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueItem
        fields = "__all__"


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = "__all__"


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
    class Meta:
        model = PackagePhoto
        fields = "__all__"


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

    photos = PackagePhotoSerializer(many=True, read_only=True)
    includes = PackageIncludeSerializer(many=True, read_only=True)
    itinerary = PackageItinerarySerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = "__all__"


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
            "status",
            "public_code",
            "created_at",
            "updated_at",
        )


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
