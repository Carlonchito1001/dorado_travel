from django.contrib import admin
from .models import *

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
    list_display = ("id","title","category","price_from","currency","difficulty","duration_days","is_popular","is_featured","is_active")
    search_fields = ("title","short_description","description","category__name")
    list_filter = ("category","difficulty","is_popular","is_featured","is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PackagePhotoInline, PackageIncludeInline, PackageItineraryInline]

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id","package","full_name","email","phone","status","total_amount","currency","created_at")
    list_filter = ("status","currency")
    search_fields = ("full_name","email","phone","public_code","package__title")

@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id","full_name","email","subject","created_at")
    search_fields = ("full_name","email","subject")

@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("id","email","is_active","created_at")
    search_fields = ("email",)

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("id","path","ip","country","created_at")
    search_fields = ("path","ip","country")
