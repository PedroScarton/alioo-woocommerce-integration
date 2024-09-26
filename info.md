fecha horas invertidas
24-09 1
25-09 2
26-09 5


Cookie:
ASP.NET_SessionId=any3sb21hxkbnvtfsxqv2cqz;
cashRegister=3071;
facility=4360;
token=0e0c4171-8ac3-4640-9d04-570ce34370fa;
user=Leandro

#### **Componentes del Script:**

1. **Módulo de Autenticación:**
   - **Descripción:** Maneja el inicio de sesión y mantiene la sesión activa.
   - **Implementación:**
     - Utilizar la librería `requests` para enviar una solicitud POST al endpoint de login con tus credenciales.
     - Almacenar el token de autenticación y las cookies en una sesión persistente.

2. **Módulo de Descarga del Excel:**
   - **Descripción:** Descarga el archivo Excel utilizando la sesión autenticada.
   - **Implementación:**
     - Realizar una solicitud GET al endpoint que proporciona el Excel, utilizando la sesión con el token y las cookies.
     - Guardar el archivo Excel en una ubicación temporal en el servidor.

3. **Módulo de Procesamiento del Excel:**
   - **Descripción:** Convierte y adapta el Excel al formato requerido por WooCommerce.
   - **Implementación:**
     - Utilizar `pandas` y `openpyxl` para leer y manipular el Excel.
     - Realizar las transformaciones necesarias (por ejemplo, ajustar nombres de columnas, formatos de datos, etc.).
     - Exportar el resultado en un formato compatible (CSV o JSON).

4. **Módulo de Integración con WooCommerce:**
   - **Descripción:** Sube o actualiza los productos en WooCommerce utilizando la API REST.
   - **Implementación:**
     - Utilizar la librería `woocommerce` para interactuar con la API.
     - Configurar las credenciales de API (Consumer Key y Consumer Secret) de forma segura.
     - Para cada producto en el archivo procesado:
       - Verificar si el producto ya existe en WooCommerce (por SKU u otro identificador único).
       - Si existe, actualizar sus datos.
       - Si no existe, crear un nuevo producto.


### **Siguiente Paso:**

- **Desarrollo del Script:**
  - Comenzar por desarrollar y probar cada módulo individualmente.
  - Una vez que cada parte funcione correctamente, integrarlas en un solo script.

- **Configuración del Entorno:**
  - Instalar Python y las librerías necesarias en tu servidor.
  - Configurar las variables de entorno y archivos de configuración.

- **Programación de la Tarea Automatizada:**
  - Una vez validado, configurar la tarea programada en tu servidor.