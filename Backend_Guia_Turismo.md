
# Backend – Guía de Turismo (Django + API REST)

Backend desarrollado con **Django** y **Django Rest Framework** para una **web/app de guía turística**, con administración desde Django Admin y consumo vía API REST.

---

## 🧱 Stack tecnológico

- Python 3.10+
- Django
- Django Rest Framework
- MySQL (Laragon)
- JWT Authentication
- Pillow (manejo de imágenes)

---

## 📁 Estructura del proyecto

```
backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── turismo/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── media/
├── manage.py
└── README.md
```

---

## ⚙️ Instalación

### Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### Instalar dependencias
```bash
pip install django djangorestframework djangorestframework-simplejwt pillow mysqlclient django-filter
```

---

## 🛢️ Base de datos (MySQL – Laragon)

### Crear base de datos
```sql
CREATE DATABASE dorado_travel
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### Configuración en `settings.py`
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "dorado_travel",
        "USER": "root",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

---

## 🧩 Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 👤 Crear superusuario

```bash
python manage.py createsuperuser
```

Panel administrativo:
```
http://127.0.0.1:8000/admin/
```

---

## ▶️ Ejecutar servidor

```bash
python manage.py runserver
```

---

## 🔐 Autenticación JWT

### Obtener token
```http
POST /api/token/
```

```json
{
  "username": "admin",
  "password": "password"
}
```

### Refresh token
```http
POST /api/token/refresh/
```

---

## 📡 Endpoints principales

### Home / Landing
- GET /api/v1/site/
- GET /api/v1/hero-slides/
- GET /api/v1/services/
- GET /api/v1/testimonials/
- GET /api/v1/faqs/
- GET /api/v1/kpis/

### Paquetes
- GET /api/v1/packages/

### Reservas
- POST /api/v1/reservations/
- GET /api/v1/my-reservations/?email=correo@ejemplo.com

---

## ℹ️ Notas

- migrate crea tablas, no datos.
- Los datos se gestionan desde Django Admin.
- Proyecto estructurado con una sola app (`turismo`).

---

## 📄 Licencia
Uso privado / educativo.
