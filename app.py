import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Importar la función create_app solo después de cargar las variables de entorno
from app import create_app

# Crear la aplicación
app = create_app()

# Ejecutar la aplicación
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)