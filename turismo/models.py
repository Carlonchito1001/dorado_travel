from django.db import models

class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class SiteInfo(Timestamped):
    brand_name = models.CharField(max_length=120, default="Dorado Travel")
    hero_title = models.CharField(max_length=200, default="Explora la Selva Profunda")
    hero_subtitle = models.CharField(max_length=240, default="Caminatas guiadas por expertos locales certificados")
    contact_email = models.EmailField(default="info@doradotravel.com")
    contact_phone = models.CharField(max_length=40, default="+51 965 853 347")
    contact_address = models.CharField(max_length=200, default="Iquitos, Loreto, Amazonía Peruana")
    whatsapp_phone = models.CharField(max_length=40, blank=True, null=True)
    horario = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuración del Sitio"

class HeroSlide(Timestamped):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=240, blank=True, null=True)
    image = models.ImageField(upload_to="hero/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class Service(Timestamped):
    title = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=60, blank=True, null=True)  # nombre de icono
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class AboutBlock(Timestamped):
    key = models.CharField(max_length=60, unique=True)  # MISION, VISION, QUIENES_SOMOS, SOSTENIBILIDAD, etc.
    title = models.CharField(max_length=160)
    body = models.TextField()
    icon = models.CharField(max_length=60, blank=True, null=True)
    image = models.ImageField(upload_to="about/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class ValueItem(Timestamped):
    title = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=60, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class TeamMember(Timestamped):
    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="team/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class Certification(Timestamped):
    title = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class KPI(Timestamped):
    key = models.CharField(max_length=60, unique=True)  # YEARS, SATISFIED, PACKAGES, SATISFACTION
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=40)  # "10+", "5000+", "98%"
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class Faq(Timestamped):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["order", "id"]

class Testimonial(Timestamped):
    full_name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True, null=True)
    comment = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["-created_at"]

class Category(Timestamped):
    name = models.CharField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Package(Timestamped):
    DIFFICULTY = [("FACIL","Fácil"),("MODERADA","Moderada"),("DIFICIL","Difícil")]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="packages")
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    short_description = models.CharField(max_length=260)
    description = models.TextField(blank=True, null=True)

    cover = models.ImageField(upload_to="packages/covers/", blank=True, null=True)

    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")

    duration_days = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=12, choices=DIFFICULTY, default="MODERADA")

    max_group = models.PositiveIntegerField(blank=True, null=True)
    activities_count = models.PositiveIntegerField(blank=True, null=True)

    is_popular = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title

class PackagePhoto(Timestamped):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="packages/photos/")
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["order", "id"]

class PackageInclude(Timestamped):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="includes")
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["order", "id"]

class PackageItinerary(Timestamped):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="itinerary")
    day = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=160)
    detail = models.TextField()
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["day", "order", "id"]

class Reservation(Timestamped):
    STATUS = [
        ("PENDIENTE","Pendiente"),
        ("CONTACTADO","Contactado"),
        ("CONFIRMADO","Confirmado"),
        ("CANCELADO","Cancelado"),
    ]

    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="reservations")
    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True, null=True)
    travel_date = models.DateField(blank=True, null=True)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS, default="PENDIENTE")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default="USD")

    public_code = models.CharField(max_length=16, unique=True)  # para buscar sin login

    class Meta:
        ordering = ["-created_at"]

class ContactMessage(Timestamped):
    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True, null=True)
    subject = models.CharField(max_length=160)
    message = models.TextField()

class NewsletterSubscriber(Timestamped):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

class PageView(Timestamped):
    path = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=80, blank=True, null=True)
