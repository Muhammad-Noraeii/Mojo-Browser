# Mojo Browser

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green)](https://pypi.org/project/PyQt5/)
[![GitHub Issues](https://img.shields.io/github/issues/Muhammad-Noraeii/Mojo-Browser)](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Muhammad-Noraeii/Mojo-Browser)](https://github.com/Muhammad-Noraeii/Mojo-Browser/stargazers)

[English Translation](README.md)

[France Translation](README-FR.md)


Un navegador web ligero centrado en la privacidad, construido con Python y PyQt5. Mojo Browser ofrece funciones de seguridad robustas, soporte para extensiones y una interfaz moderna y personalizable.

---

## Tabla de Contenido

- [Características](#features)
- [Instalación](#installation)
- [Uso](#usage)
- [Contribución](#contributing)
- [Licencia](#license)
- [Agradecimientos](#acknowledgements)
- [Contacto](#contact)

---

## Características

- **Privacidad y Seguridad**: Bloqueo de rastreadores, soporte de proxy, aplicación de HTTPS y anti-huella digital.
- **Extensiones**: Carga extensiones JavaScript desde MojoX o fuentes personalizadas.
- **Temas**: Opciones de tema Oscuro, Claro o Sistema.
- **Rendimiento**: Aceleración de hardware, suspensión de pestañas y límites de caché configurables.
- **Motores de Búsqueda**: Admite Google, DuckDuckGo, Mojeek y más.
- **Extras**: Modo lector, marcadores, historial y administrador de descargas.

---

## Instalación

### Requisitos Previos
- **Python**: 3.8 o superior
- **Dependencias**: PyQt5, PyQtWebEngine, Requests

### Pasos
1. **Clonar el Repositorio**:
   ```bash
   git clone https://github.com/Muhammad-Noraeii/Mojo-Browser.git
   cd Mojo-Browser
   ```

2. **Instalar Dependencias**:
   ```bash
   pip install PyQt5 PyQtWebEngine requests
   ```
   Alternativamente, si se agrega un archivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar el Navegador**:
   ```bash
   python main.py
   ```

4. **Opcional**: Agrega iconos a una carpeta `icons/` (por ejemplo, `app_icon.png`) para una experiencia de IU completa.

---

## Uso

- Inicia el navegador con `python main.py`.
- Utiliza la barra de herramientas para navegar, administrar pestañas o acceder a la configuración.
- Configura las opciones de privacidad, los temas y las extensiones a través del menú Configuración.
- Haz doble clic en los marcadores o elementos del historial para visitar las URL guardadas.

Para obtener controles detallados, consulta la sección [atajos](#shortcuts) a continuación.

### Atajos
- `Ctrl+T`: Nueva pestaña
- `Ctrl+W`: Cerrar pestaña
- `Ctrl+R` o `F5`: Recargar página
- `F11`: Alternar pantalla completa
- `Ctrl+Shift+R`: Alternar modo lector

---

## Contribución

¡Damos la bienvenida a las contribuciones! Así es como puedes empezar:

1. **Bifurca el Repositorio**: Haz clic en "Fork" en GitHub.
2. **Clona Tu Bifurcación**:
   ```bash
   git clone https://github.com/TU_USUARIO/Mojo-Browser.git
   ```
3. **Crea una Rama**:
   ```bash
   git checkout -b feature/nombre-de-tu-caracteristica
   ```
4. **Confirma los Cambios**:
   ```bash
   git commit -m "Añade tu mensaje aquí"
   ```
5. **Sube a Tu Bifurcación**:
   ```bash
   git push origin feature/nombre-de-tu-caracteristica
   ```
6. **Envía una Solicitud de Extracción (Pull Request)**: Abre una PR en el repositorio principal.

Por favor, lee nuestras [Directrices de Contribución](CONTRIBUTING.md) para obtener más detalles.

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.

---

## Agradecimientos

- **Equipo de PyQt5**: Por el potente framework de GUI.
- **Colaboradores**: [Muhammad-Noraeii](https://github.com/Muhammad-Noraeii), [Guguss-31](https://github.com/Guguss-31).
- **Comunidad**: ¡Gracias a todos los usuarios y probadores!

---

## Contacto

- **Mantenedor**: [Muhammad Noraeii](https://github.com/Muhammad-Noraeii)
- **Problemas**: Informa sobre errores o sugiere características [aquí](https://github.com/Muhammad-Noraeii/Mojo-Browser/issues).
- **Correo electrónico**: Muhammad.Noraeii@gmail.com

---

¡Gracias por usar Mojo Browser!

¡Dale una estrella al proyecto si te gusta! ⭐
