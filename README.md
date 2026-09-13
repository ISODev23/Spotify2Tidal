# Spotify2Tidal

Herramienta en Python para migrar tus playlists de **Spotify** a **Tidal** de forma local, rápida y sin limitaciones ni muros de pago.

> **Créditos:** Este proyecto es una versión mejorada e inspirada en el repositorio original [taschenb/spotify2tidal](https://github.com/taschenb/spotify2tidal.git).

---

## Mejoras
* **Autenticación Actualizada:** Se corrigió y actualizó el método de autenticación con Tidal para garantizar compatibilidad y estabilidad.
* **Selección Interactiva de Playlists:** Obtiene el listado completo de playlists vinculadas a tu cuenta de Spotify y las presenta en un menú enumerado. Solo seleccionas el número de índice de la lista que deseas transferir.
* **Flujo OAuth Eficiente:** En el primer uso se abrirá una ventana en el navegador para autorizar el acceso en ambas plataformas. Las credenciales de sesión se guardan localmente para no solicitar autenticación en posteriores ejecuciones.
* El proyecto contiene un ejecutable directo para su uso en el directorio [Spotify2Tidal](https://github.com/ISODev23/Spotify2Tidal/tree/39cb43023dc091c860738f538878ab458868382e/ejecutable)

---

### Instrucciones de uso rápido

1. Descarga y extrae el archivo comprimido:
   ```bash
   tar -xvf spotify2tidal-linux.tar.gz
   cd spotify2tidal-linux 

---

## Requisitos Previos

* Cuenta activa en Spotify developer y Tidal.

---

## Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/spotify2tidal.git](https://github.com/tu-usuario/spotify2tidal.git)
   cd spotify2tidal
