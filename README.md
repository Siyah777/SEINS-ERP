# SEINS-ERP

**SEINS-ERP** es un sistema **ERP de código abierto** diseñado para **empresas de ingeniería, mantenimiento industrial y logística**, especialmente aquellas que requieren control técnico, trazabilidad operativa y escalabilidad.

El proyecto nace de la experiencia real en **mantenimiento, metrología y operación de sistemas críticos**, y busca cerrar la brecha entre la gestión administrativa y la realidad técnica del campo.

Está construido con **Django**, **PostgreSQL** y **Docker**, bajo una arquitectura **modular, extensible y orientada a producción**.

---

## 🎯 Objetivo del proyecto

Proveer una plataforma ERP que permita a empresas técnicas:

* Gestionar **inventarios, ventas y facturación** de forma integrada.
* Administrar **mantenimiento, proyectos y órdenes de trabajo**.
* Centralizar información técnica para **mejorar la toma de decisiones**.
* Servir como base para **digitalización de procesos de ingeniería**.

SEINS-ERP no es un proyecto académico; es un sistema pensado para **uso real**, con despliegues en entornos productivos.

---

## 🚀 Características principales

* 📦 **Inventarios**
  Gestión de repuestos, existencias y control de stock.

* 🧾 **Ventas y Facturación**
  Generación de documentos comerciales e integración con **facturación electrónica (DTE – El Salvador)**.

* 🛠 **Mantenimiento y Proyectos**
  Órdenes de trabajo, seguimiento de actividades, historial y reportes técnicos.

* 🧩 **Arquitectura modular**
  Cada módulo puede evolucionar de forma independiente.

* 🔐 **Seguridad y roles**
  Gestión de usuarios y permisos basada en roles.

* ☁️ **Listo para producción**
  Desplegado en entornos reales usando contenedores Docker.

---

## 🏗️ Arquitectura (visión general)

SEINS-ERP utiliza una arquitectura clásica y robusta:

* **Backend**: Django + Django REST Framework
* **Base de datos**: PostgreSQL
* **Infraestructura**: Docker / Docker Compose
* **Servidor web**: Apache + WSGI (Waitress)
* **Frontend**:

  * Django Admin para administradores internos
  * React (en desarrollo) para clientes y proveedores

Esta arquitectura permite escalar el sistema y adaptarlo a distintos contextos empresariales.

---

## 📦 Instalación rápida (Docker)

> Recomendado para entornos de prueba y producción controlada.

```bash
git clone https://github.com/Siyah777/seins-erp.git
mv seins-erp SEINSERP
cd SEINSERP
docker compose -f docker-compose.prod.yml up -d --build
```

Asegúrate de configurar correctamente las **variables de entorno** antes del despliegue.

---

## 🧪 Estado del proyecto

SEINS-ERP se encuentra en **desarrollo activo**, con módulos funcionales y otros en evolución.

✔ Inventarios
✔ Ventas y facturación básica
✔ Mantenimiento / OT
🚧 Indicadores, analítica y automatizaciones avanzadas

---

## 🌐 Proyectos en producción

* Sitio corporativo: [https://seinsv.com](https://seinsv.com)
* Plataforma activa: [https://seinsv.online](https://seinsv.online)

Estos entornos demuestran el uso real del sistema en producción.

---

## 🧑‍💻 Contribuciones

Las contribuciones son bienvenidas.

Antes de enviar un PR:

* Revisa la **Guía de Contribución** (próximamente).
* Respeta el **Código de Conducta** del proyecto.
* Documenta los cambios realizados.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License**.
Consulta el archivo `LICENSE` para más detalles.

---

## 👤 Autor y contacto

**Sergio Erazo**
Ingeniero Mecánico | Software & Cloud Engineering

* GitHub: [https://github.com/Siyah777](https://github.com/Siyah777)
* Proyecto: [https://github.com/Siyah777/SEINS-ERP](https://github.com/Siyah777/SEINS-ERP)
* Sitio web: [https://seinsv.com](https://seinsv.com)

---

> SEINS-ERP representa la convergencia entre ingeniería, operación y tecnología.
> Construido desde la experiencia real, no desde la teoría.

