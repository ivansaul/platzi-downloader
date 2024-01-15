![Repo Banner](https://i.imgur.com/I6zFXds.png)

<div align="center">

<h1 style="border-bottom: none">
    <b><a href="#">Platzi Downloader</a></b>
</h1>

Descarga automática de los cursos de `Platzi` con un script creado en `Python` utilizando `yt-dlp` como un subproceso.

![GitHub repo size](https://img.shields.io/github/repo-size/ivansaul/platzi-downloader)
![GitHub stars](https://img.shields.io/github/stars/ivansaul/platzi-downloader)
![GitHub forks](https://img.shields.io/github/forks/ivansaul/platzi-downloader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![Discord](https://img.shields.io/badge/-Discord-424549?style=social&logo=discord)](https://discord.gg/tDvybtJ7y9)

</div>

---

## Instalación

El script utiliza **Selenium & Google Chrome (chrome driver)**, así que asegúrate de tener instalado y actualizado **Chrome browser** en tu ordenador.

```bash
git clone https://github.com/ivansaul/platzi-downloader.git
cd platzi-downloader
pip install -r requirements.txt
```

### **Linux**

**En Ubuntu:**

```bash
sudo apt update -y
# Install Google Chrome ...
sudo apt install ffmpeg aria2 -y
pip install -U yt-dlp
```

**En Archlinux:**

```bash
sudo pacman -Syu
sudo pacman -S ffmpeg aria2 yt-dlp
yay -S google-chrome
```

### **Windows**

> **Nota:** Asegurate de tener instalados [Python][python], [Google Chrome][chrome] , [yt-dlp][yt-dlp] y [ffmpeg][ffmpeg].

```bash
# Install Python ...
# Install ffmpeg ...
# Install Google Chrome ...
pip install -U yt-dlp
```

## Instrucciones

1. Ejecuta el script `platzi.py` para obtener las url de los videos. 

```bash
python platzi.py
```

El script te pedirá tu correo y contraseña, así como la URL del curso a descargar (la URL puede ser de cualquier video del curso).

```bash
Ingresa tus credenciales de Platzi
Ingresa tu e-mail: tu@email.com
Ingresa tu contraseña: tu_comtraseña
Ingresa la URL del curso a descargar: https://platzi.com/clases/2292-terminal/37344-manipulando-archivos-y-directorios/
.
.
.
```

2. Finalmente para descargar los vídeos ejecute.

```bash
python downloader.py
```

Por defecto, los vídeos se descargarán automáticamente en una carpeta con el mismo nombre del curso, con la mejor calidad existente (`best`) y usando `aria2` como gestor de descargas. Para personalizar la descarga, puedes usar las siguientes opciones.

```bash
Usage: python downloader.py [OPTIONS]

Options:
  -d [yt-dlp|wget|aria2]      Select the external downloader (yt-dlp, or aria2). Default: aria2.
  -q [360|480|720|1080|best]  Select the video quality (360, 480, 720, 1080 or best). Default: best
  --help                      Show this message and exit.

Examples: 
  python downloader.py -q 1080
  python downloader.py -d yt-dlp
  python downloader.py -d yt-dlp -q 720
  python downloader.py --help
```

> **Nota:** Si por algún motivo se cancela la descarga, vuelve a ejecutar `python downloader.py [OPTIONS]` para retomar la descarga.



# **Aviso de Uso**

Este proyecto se realiza con fines exclusivamente educativos y de aprendizaje. El código proporcionado se ofrece "tal cual", sin ninguna garantía de su funcionamiento o idoneidad para ningún propósito específico.

No me hago responsable por cualquier mal uso, daño o consecuencia que pueda surgir del uso de este proyecto. Es responsabilidad del usuario utilizarlo de manera adecuada y dentro de los límites legales y éticos.


[python]: https://www.python.org/downloads/
[ffmpeg]: https://ffmpeg.org
[chrome]: https://www.google.com/chrome/
[yt-dlp]: https://github.com/yt-dlp/yt-dlp/wiki/Installation
[aria2]: https://github.com/aria2/aria2/releases/tag/release-1.36.0
[demo]: https://youtu.be/GbQwB0hYvQU
[ffmpeg-win]:https://youtu.be/0zN9oZ98ZgE
