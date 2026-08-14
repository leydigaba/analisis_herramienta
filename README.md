# analisis_herramienta

## Crear y activar el entorno virtual

Crea el entorno virtual:

```bash
python3 -m venv venv
```

Activa el entorno virtual:

```bash
source venv/bin/activate
```
## Instalación de dependencias

Instala todas las dependencias del proyecto con:

```bash
pip install -r requirements.txt
```

Dependencias principales utilizadas:
```
- Flask
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Pillow
```
## Dockerfile
 
El `Dockerfile` contiene las instrucciones para construir la imagen:
 
```dockerfile
FROM ubuntu:24.04
 
LABEL maintainer="leydi12"
LABEL version="0.1"
LABEL description="Contenedor para analisis de datos"
 
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3 python3-pip
 
WORKDIR /analisis_herramienta
 
COPY requirements.txt .
RUN pip install -r requirements.txt --break-system-packages
 
COPY primero.py .
 
EXPOSE 5000
 
CMD ["python3", "primero.py"]
```
 
---
 
## Despliegue con Docker
 
Construye la imagen:
 
```bash
docker build -t leydi12/analisis_herramienta:0.1 .
```
 
Verifica que la imagen se creó:
 
```bash
docker images
```
 
Ejecuta el contenedor:
 
```bash
docker run -d -p 5000:5000 --name analisis_app leydi12/analisis_herramienta:0.1
```
 
Verifica que está corriendo:
 
```bash
docker ps
```
 
Abre en el navegador:
 
```
http://localhost:5000
```
 
---
 
## Subir imagen a Docker Hub
 
Inicia sesión:
 
```bash
docker login
```
 
Sube la imagen:
 
```bash
docker push leydi12/analisis_herramienta:0.1
```
 
La imagen queda disponible en:
 
```
https://hub.docker.com/r/leydi12/analisis_herramienta
```
 
---
 
## Descargar y correr desde Docker Hub
 
Cualquier persona con Docker instalado puede correr el proyecto con:
 
```bash
docker pull leydi12/analisis_herramienta:0.1
```
 
```bash
docker run -d -p 5000:5000 --name analisis_app leydi12/analisis_herramienta:0.1
```
 
---
 
## Comandos útiles
 
| Comando | Descripción |
|---|---|
| `docker images` | Ver imágenes descargadas |
| `docker ps` | Ver contenedores corriendo |
| `docker ps -a` | Ver todos los contenedores |
| `docker stop analisis_app` | Detener el contenedor |
| `docker rm analisis_app` | Eliminar el contenedor |
| `docker logs analisis_app` | Ver logs del contenedor |