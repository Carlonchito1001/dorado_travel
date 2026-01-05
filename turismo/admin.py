from django.contrib import admin
from .models import (
    SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember,
    Certification, KPI, Faq, Testimonial, Category,
    Package, PackagePhoto, PackageInclude, PackageItinerary,
    Reservation, ContactMessage, NewsletterSubscriber, PageView,
    Cart, CartItem, Payment
)

@admin.register(SiteInfo, HeroSlide, Service, AboutBlock, ValueItem, TeamMember, Certification, KPI, Faq, Testimonial, Category)
class SimpleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    search_fields = ("id",)


class PackagePhotoInline(admin.TabularInline):
    model = PackagePhoto
    extra = 1


class PackageIncludeInline(admin.TabularInline):
    model = PackageInclude
    extra = 1


class PackageItineraryInline(admin.TabularInline):
    model = PackageItinerary
    extra = 1


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price_from", "currency", "difficulty", "duration_days", "is_popular", "is_featured", "is_active")
    search_fields = ("title", "short_description", "description", "category__name")
    list_filter = ("category", "difficulty", "is_popular", "is_featured", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PackagePhotoInline, PackageIncludeInline, PackageItineraryInline]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "package", "full_name", "email", "phone", "nationality", "status", "total_amount", "currency", "public_code", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("full_name", "email", "phone", "public_code", "package__title")


@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "subject", "created_at")
    search_fields = ("full_name", "email", "subject")


@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_active", "created_at")
    search_fields = ("email",)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("id", "path", "ip", "country", "created_at")
    search_fields = ("path", "ip", "country")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ("package", "reservation", "travel_date", "adults", "children", "unit_price", "currency", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "nationality", "status", "expires_at", "created_at")
    list_filter = ("status",)
    search_fields = ("email", "phone")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "amount", "currency", "provider", "status", "reference", "created_at")
    list_filter = ("status", "provider", "currency")
    search_fields = ("reference", "cart__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "package", "reservation", "adults", "children", "unit_price", "currency", "created_at")
    list_filter = ("currency",)
    search_fields = ("cart__email", "package__title", "reservation__public_code")
    readonly_fields = ("created_at", "updated_at")
