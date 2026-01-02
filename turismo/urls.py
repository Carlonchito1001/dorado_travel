from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SiteInfoViewSet,
    HeroSlideViewSet,
    ServiceViewSet,
    AboutBlockViewSet,
    ValueItemViewSet,
    TeamMemberViewSet,
    CertificationViewSet,
    KPIViewSet,
    FaqViewSet,
    TestimonialViewSet,
    CategoryViewSet,
    PackageViewSet,
    ReservationViewSet,
    ContactMessageViewSet,
    NewsletterSubscriberViewSet,
    my_reservations_lookup,
    track_pageview,
    admin_dashboard,
)

router = DefaultRouter()

# ---- Configuración / Home ----
router.register("site", SiteInfoViewSet, basename="site")
router.register("hero-slides", HeroSlideViewSet, basename="hero-slides")
router.register("services", ServiceViewSet, basename="services")

# ---- Contenido institucional ----
router.register("about-blocks", AboutBlockViewSet, basename="about-blocks")
router.register("values", ValueItemViewSet, basename="values")
router.register("team", TeamMemberViewSet, basename="team")
router.register("certifications", CertificationViewSet, basename="certifications")
router.register("kpis", KPIViewSet, basename="kpis")
router.register("faqs", FaqViewSet, basename="faqs")
router.register("testimonials", TestimonialViewSet, basename="testimonials")

# ---- Catálogo ----
router.register("categories", CategoryViewSet, basename="categories")
router.register("packages", PackageViewSet, basename="packages")

# ---- Reservas ----
router.register("reservations", ReservationViewSet, basename="reservations")

# ---- Contacto / Newsletter ----
router.register("contact-messages", ContactMessageViewSet, basename="contact-messages")
router.register("newsletter", NewsletterSubscriberViewSet, basename="newsletter")

urlpatterns = [
    # API REST
    path("v1/", include(router.urls)),

    # Endpoints adicionales
    path("v1/my-reservations/", my_reservations_lookup, name="my-reservations"),
    path("v1/track-pageview/", track_pageview, name="track-pageview"),

    # Dashboard admin
    path("v1/admin/dashboard/", admin_dashboard, name="admin-dashboard"),
]
