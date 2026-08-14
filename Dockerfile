FROM ubuntu:24.04

# Informacion de la imagen
LABEL maintainer="leydi12"
LABEL version="0.1"
LABEL description="Contenedor para analisis de datos"

# Instalar paquetes
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3 python3-pip

# Carpeta de trabajo
WORKDIR /analisis_herramienta

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt --break-system-packages

# Copiar aplicacion
COPY primero.py .

EXPOSE 5000

CMD ["python3", "primero.py"]