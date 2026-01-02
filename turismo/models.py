from django.db import models
import secrets
from django.utils import timezone



# ======================================================
# BASE ABSTRACTA
# ======================================================
class Timestamped(models.Model):
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)

    class Meta:
        abstract = True


# ======================================================
# CONFIGURACIÓN GENERAL DEL SITIO
# ======================================================
class SiteInfo(Timestamped):
    brand_name = models.CharField("Nombre de la marca", max_length=120, default="Dorado Travel")
    hero_title = models.CharField("Título principal", max_length=200, default="Explora la Selva Profunda")
    hero_subtitle = models.CharField("Subtítulo principal", max_length=240)
    contact_email = models.EmailField("Correo de contacto")
    contact_phone = models.CharField("Teléfono", max_length=40)
    contact_address = models.CharField("Dirección", max_length=200)
    whatsapp_phone = models.CharField("WhatsApp", max_length=40, blank=True, null=True)
    horario = models.CharField("Horario de atención", max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuraciones del sitio"


class HeroSlide(Timestamped):
    title = models.CharField("Título", max_length=200)
    subtitle = models.CharField("Subtítulo", max_length=240, blank=True, null=True)
    image = models.ImageField("Imagen", upload_to="hero/")
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Slide principal"
        verbose_name_plural = "Slides principales"
        ordering = ["order", "id"]


class Service(Timestamped):
    title = models.CharField("Título", max_length=120)
    description = models.TextField("Descripción")
    icon = models.CharField("Ícono", max_length=60, blank=True, null=True)
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["order", "id"]


# ======================================================
# CONTENIDO INSTITUCIONAL
# ======================================================
class AboutBlock(Timestamped):
    key = models.CharField(
        "Clave",
        max_length=60,
        unique=True,
        help_text="Ej: MISION, VISION, QUIENES_SOMOS"
    )
    title = models.CharField("Título", max_length=160)
    body = models.TextField("Contenido")
    icon = models.CharField("Ícono", max_length=60, blank=True, null=True)
    image = models.ImageField("Imagen", upload_to="about/", blank=True, null=True)
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Bloque informativo"
        verbose_name_plural = "Bloques informativos"
        ordering = ["order", "id"]


class ValueItem(Timestamped):
    title = models.CharField("Título", max_length=120)
    description = models.TextField("Descripción")
    icon = models.CharField("Ícono", max_length=60, blank=True, null=True)
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Valor"
        verbose_name_plural = "Valores"
        ordering = ["order", "id"]


class TeamMember(Timestamped):
    full_name = models.CharField("Nombre completo", max_length=120)
    role = models.CharField("Cargo", max_length=120)
    bio = models.TextField("Biografía", blank=True, null=True)
    avatar = models.ImageField("Foto", upload_to="team/", blank=True, null=True)
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Miembro del equipo"
        verbose_name_plural = "Equipo"
        ordering = ["order", "id"]


class Certification(Timestamped):
    title = models.CharField("Certificación", max_length=160)
    issuer = models.CharField("Entidad emisora", max_length=160, blank=True, null=True)
    year = models.PositiveIntegerField("Año", blank=True, null=True)
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Certificación"
        verbose_name_plural = "Certificaciones"
        ordering = ["order", "id"]


class KPI(Timestamped):
    key = models.CharField("Clave", max_length=60, unique=True)
    label = models.CharField("Etiqueta", max_length=120)
    value = models.CharField("Valor", max_length=40)
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"
        ordering = ["order", "id"]


class Faq(Timestamped):
    question = models.CharField("Pregunta", max_length=200)
    answer = models.TextField("Respuesta")
    order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Pregunta frecuente"
        verbose_name_plural = "Preguntas frecuentes"
        ordering = ["order", "id"]


class Testimonial(Timestamped):
    full_name = models.CharField("Nombre", max_length=120)
    location = models.CharField("Ubicación", max_length=120, blank=True, null=True)
    comment = models.TextField("Comentario")
    rating = models.PositiveIntegerField("Calificación", default=5)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Testimonio"
        verbose_name_plural = "Testimonios"
        ordering = ["-created_at"]


# ======================================================
# CATÁLOGO DE PAQUETES
# ======================================================
class Category(Timestamped):
    name = models.CharField("Nombre", max_length=80, unique=True)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Package(Timestamped):
    DIFFICULTY = [
        ("FACIL", "Fácil"),
        ("MODERADA", "Moderada"),
        ("DIFICIL", "Difícil"),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="packages",
        verbose_name="Categoría"
    )

    title = models.CharField("Título", max_length=160)
    slug = models.SlugField("Slug", max_length=180, unique=True)
    short_description = models.CharField("Descripción corta", max_length=260)
    description = models.TextField("Descripción completa", blank=True, null=True)

    cover = models.ImageField("Imagen principal", upload_to="packages/covers/", blank=True, null=True)

    price_from = models.DecimalField("Precio por persona", max_digits=10, decimal_places=2)
    currency = models.CharField("Moneda", max_length=10, default="USD")

    duration_days = models.PositiveIntegerField("Duración (días)", default=1)
    difficulty = models.CharField("Dificultad", max_length=12, choices=DIFFICULTY, default="MODERADA")

    max_group = models.PositiveIntegerField("Máx. personas", blank=True, null=True)
    activities_count = models.PositiveIntegerField("Cantidad de actividades", blank=True, null=True)

    is_popular = models.BooleanField("Popular", default=False)
    is_featured = models.BooleanField("Destacado", default=False)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Paquete turístico"
        verbose_name_plural = "Paquetes turísticos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PackagePhoto(Timestamped):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Paquete"
    )
    image = models.ImageField("Imagen", upload_to="packages/photos/")
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Foto del paquete"
        verbose_name_plural = "Fotos del paquete"
        ordering = ["order", "id"]


class PackageInclude(Timestamped):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="includes",
        verbose_name="Paquete"
    )
    text = models.CharField("Incluye", max_length=200)
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Incluye"
        verbose_name_plural = "Incluye"
        ordering = ["order", "id"]


class PackageItinerary(Timestamped):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="itinerary",
        verbose_name="Paquete"
    )
    day = models.PositiveIntegerField("Día")
    title = models.CharField("Título", max_length=160)
    detail = models.TextField("Detalle")
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Itinerario"
        verbose_name_plural = "Itinerarios"
        ordering = ["day", "order", "id"]


# ======================================================
# RESERVAS
# ======================================================
class Reservation(Timestamped):
    STATUS = [
        ("PENDIENTE", "Pendiente"),
        ("CONTACTADO", "Contactado"),
        ("CONFIRMADO", "Confirmado"),
        ("CANCELADO", "Cancelado"),
    ]

    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="Paquete"
    )

    full_name = models.CharField("Nombre completo", max_length=140)
    email = models.EmailField("Correo electrónico")
    phone = models.CharField("Teléfono", max_length=40, blank=True, null=True)

    travel_date = models.DateField("Fecha de viaje", blank=True, null=True)
    adults = models.PositiveIntegerField("Adultos", default=1)
    children = models.PositiveIntegerField("Niños", default=0)

    notes = models.TextField("Notas", blank=True, null=True)

    status = models.CharField("Estado", max_length=20, choices=STATUS, default="PENDIENTE")

    total_amount = models.DecimalField(
        "Monto total",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    currency = models.CharField("Moneda", max_length=10, default="USD")

    public_code = models.CharField(
        "Código público",
        max_length=16,
        unique=True,
        help_text="Código para que el cliente consulte su reserva"
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-created_at"]


# ======================================================
# CONTACTO / NEWSLETTER / TRACKING
# ======================================================
class ContactMessage(Timestamped):
    full_name = models.CharField("Nombre completo", max_length=140)
    email = models.EmailField("Correo")
    phone = models.CharField("Teléfono", max_length=40, blank=True, null=True)
    subject = models.CharField("Asunto", max_length=160)
    message = models.TextField("Mensaje")

    class Meta:
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"


class NewsletterSubscriber(Timestamped):
    email = models.EmailField("Correo", unique=True)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"


class PageView(Timestamped):
    path = models.CharField("Ruta", max_length=200)
    ip = models.GenericIPAddressField("IP", blank=True, null=True)
    user_agent = models.CharField("Navegador", max_length=255, blank=True, null=True)
    country = models.CharField("País", max_length=80, blank=True, null=True)

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
