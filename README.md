# Fletes Oriente - Cotizador y Rutas para Camión 350

Aplicación móvil híbrida para el cálculo de rutas óptimas, consumo de combustible y cotizaciones en tiempo real para fletes en **Camión 350** en todo el Oriente de Venezuela (Anzoátegui, Monagas, Sucre y Bolívar).

---

## 🚀 Características
* **Motor de Grafos y Dijkstra en C/C++:** Cálculo instantáneo de la ruta más corta/eficiente a través de las troncales viales de Oriente.
* **Modelo Tarifario Especializado:** Ajuste por porcentaje de carga (0% a 100% batea / ~3.500 kg), tarifas por km, tarifa de arranque y retorno.
* **100% Offline:** Funciona en carretera sin necesidad de conexión a internet ni datos móviles.
* **Exportación de Documentos:** Generación automática de comprobantes oficiales en **Microsoft Word (`.docx`)** y **PDF**.

---

## 🛠️ Tecnologías Utilizadas
* **C++17:** Motor de enrutamiento y grafos viales de alto rendimiento.
* **Python 3:** Lógica de cálculo, puente C-ABI (`ctypes`) y generación de documentos (`python-docx`, `fpdf2`).
* **Flet (Flutter UI):** Interfaz móvil táctil moderna con diseño Material Design 3.

---

## 📲 Compilación del APK para Android
Este repositorio cuenta con un flujo automatizado de **GitHub Actions** en `.github/workflows/build_apk.yml` que compila automáticamente el archivo `.apk` de Android con cada actualización.
