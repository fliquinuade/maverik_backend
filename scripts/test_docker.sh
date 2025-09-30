#!/bin/bash

echo "🚀 Construyendo y probando el contenedor de Maverik Backend..."

# Detener contenedores existentes
echo "📦 Deteniendo contenedores existentes..."
docker compose down

# Construir e iniciar contenedores
echo "🔨 Construyendo e iniciando contenedores..."
docker compose up --build -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar que el contenedor está ejecutándose
echo "🔍 Verificando estado de contenedores..."
docker compose ps

# Probar el endpoint de health
echo "🏥 Probando endpoint de health..."
curl -f http://localhost:8082/health || echo "❌ Health check falló"

# Probar el endpoint raíz
echo "🌐 Probando endpoint raíz..."
curl -f http://localhost:8082/ || echo "❌ Endpoint raíz falló"

# Mostrar logs si hay problemas
echo "📋 Últimos logs del backend:"
docker compose logs --tail=20 backend

echo "✅ Prueba completada. Si no hay errores, el contenedor está funcionando correctamente."