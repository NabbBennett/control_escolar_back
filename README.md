# Sistema de Control Escolar DESIT

Sistema integral de gestión escolar desarrollado con Angular y Django REST Framework, diseñado para administrar usuarios, alumnos, maestros y materias de una institución educativa.

## Descripción

Sistema web full-stack que permite la gestión completa de:
- **Administradores**: Gestión de personal administrativo
- **Alumnos**: Registro y administración de estudiantes con matrícula, CURP, RFC, etc.
- **Maestros**: Control de profesores con área de investigación, cubículo y asignación de materias
- **Materias**: Gestión de cursos con NRC, horarios, salones y programas educativos
- **Estadísticas**: Dashboard con gráficas de datos del sistema

## Arquitectura del Proyecto

### Frontend - Angular
```
src/
├── app/
│   ├── layouts/          # Layouts principales (auth, dashboard)
│   ├── screens/          # Pantallas principales
│   │   ├── login-screen/
│   │   ├── home-screen/
│   │   ├── admin-screen/
│   │   ├── alumnos-screen/
│   │   ├── maestros-screen/
│   │   ├── materia-screen/
│   │   ├── graficas-screen/
│   │   └── registro-usuarios-screen/
│   ├── partials/         # Componentes reutilizables
│   │   ├── navbar-user/
│   │   ├── sidebar/
│   │   ├── registro-admin/
│   │   ├── registro-alumnos/
│   │   └── registro-maestros/
│   ├── modals/           # Modales
│   └── services/         # Servicios HTTP y utilidades
└── environments/         # Configuración de entornos
```

### Backend - Django 
```
control_escolar_back/
├── control_escolar_desit_api/
│   ├── models.py         # Modelos: Administradores, Alumnos, Maestros, Materias
│   ├── serializers.py    # Serializadores DRF
│   ├── views/            # Vistas organizadas por módulo
│   │   ├── auth.py       # Autenticación (login/logout)
│   │   ├── users.py      # Gestión de administradores
│   │   ├── alumnos.py    # CRUD de alumnos
│   │   ├── maestros.py   # CRUD de maestros
│   │   └── materias.py   # CRUD de materias y estadísticas
│   ├── puentes/
│   │   └── mail.py       # Utilidades de correo
│   └── migrations/       # Migraciones de base de datos
└── requirements.txt      # Dependencias Python
```

### Base de Datos
- **MySQL** - Base de datos relacional
  - Database: `control_escolar_desit_db`
  - Host: 127.0.0.1:3306

## Instalación

### Requisitos Previos
- Node.js (v16 o superior)
- Python 3.10+
- MySQL Server
- Angular CLI: `npm install -g @angular/cli`

### Configuración del Backend

1. **Navegar al directorio del backend:**
```powershell
cd control_escolar_back
```

2. **Crear entorno virtual:**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. **Instalar dependencias:**
```powershell
pip install -r requirements.txt
```

4. **Configurar base de datos:**
   - Editar `my.cnf` con tus credenciales de MySQL:
```ini
[client]
host=127.0.0.1
port=3306
database=control_escolar_desit_db
user=root
password=tu_password
default-character-set=utf8mb4
```

5. **Crear base de datos:**
```sql
CREATE DATABASE control_escolar_desit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Ejecutar migraciones:**
```powershell
python manage.py migrate
```

7. **Crear superusuario (opcional):**
```powershell
python manage.py createsuperuser
```

8. **Iniciar servidor de desarrollo:**
```powershell
python manage.py runserver
```
El backend estará disponible en `http://127.0.0.1:8000`

### Configuración del Frontend

1. **Instalar dependencias:**
```powershell
npm install
```

2. **Configurar entorno:**
   - Verificar `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  url_api: "http://127.0.0.1:8000"
};
```

3. **Iniciar servidor de desarrollo:**
```powershell
npm start
```
La aplicación estará disponible en `http://localhost:4200`

## Autenticación

El sistema utiliza autenticación basada en tokens Bearer:
- **Login**: `POST /login/`
- **Logout**: `POST /logout/`
- **Headers requeridos**: `Authorization: Bearer {token}`

Las cookies almacenadas incluyen:
- `control-escolar-token`: Token de autenticación
- `control-escolar-email`: Email del usuario
- `control-escolar-user_id`: ID del usuario
- `control-escolar-user_complete_name`: Nombre completo
- `control-escolar-group_name`: Rol del usuario

## 📡 API Endpoints

### Usuarios y Administradores
- `POST /admin/` - Crear administrador
- `GET /lista-admins/` - Listar administradores
- `GET /total-usuarios/` - Total de usuarios

### Alumnos
- `POST /alumnos/` - Crear alumno
- `GET /lista-alumnos/` - Listar alumnos
- `PUT /alumnos/{id}/` - Actualizar alumno
- `DELETE /alumnos/{id}/` - Eliminar alumno

### Maestros
- `POST /maestros/` - Crear maestro
- `GET /lista-maestros/` - Listar maestros
- `PUT /maestros/{id}/` - Actualizar maestro
- `DELETE /maestros/{id}/` - Eliminar maestro

### Materias
- `POST /materias/` - Crear materia
- `GET /lista-materias/` - Listar materias
- `GET /verificar-nrc/` - Verificar NRC único
- `GET /materias-por-dia/` - Estadísticas por día
- `PUT /materias/{id}/` - Actualizar materia
- `DELETE /materias/{id}/` - Eliminar materia

### Autenticación
- `POST /login/` - Iniciar sesión
- `POST /logout/` - Cerrar sesión

## Modelos de Datos

### Administradores
- `clave_admin`: Clave única
- `telefono`, `rfc`, `edad`, `ocupacion`
- Relación con `User` de Django

### Alumnos
- `matricula`: Matrícula del estudiante
- `curp`, `rfc`: Identificación oficial
- `fecha_nacimiento`, `edad`
- `telefono`, `ocupacion`

### Maestros
- `id_trabajador`: ID de empleado
- `cubiculo`: Ubicación del cubículo
- `area_investigacion`: Área de especialización
- `materias_json`: Materias asignadas (JSON)
- `fecha_nacimiento`, `telefono`, `rfc`

### Materias
- `nrc`: Número de Referencia del Curso (único)
- `nombre`, `seccion`, `creditos`
- `dias`: Array JSON de días de la semana
- `hora_inicio`, `hora_fin`
- `salon`, `programa_educativo`
- `profesor`: ForeignKey a Maestros

## Características del Frontend

### Rutas Principales
- `/login` - Pantalla de inicio de sesión
- `/home` - Dashboard principal
- `/administrador` - Gestión de administradores
- `/alumnos` - Gestión de alumnos
- `/maestros` - Gestión de maestros
- `/materias` - Gestión de materias
- `/graficas` - Visualización de estadísticas
- `/registro-usuarios` - Registro de nuevos usuarios

### Componentes Destacados
- **Dashboard Layout**: Navegación con sidebar y navbar
- **Auth Layout**: Layout para login y registro
- **Formularios Dinámicos**: Registro diferenciado por rol
- **Tablas con Material**: Paginación y filtrado
- **Gráficas Interactivas**: Chart.js con estadísticas
- **Modales de Confirmación**: Para eliminación de registros

## Scripts Disponibles

### Frontend
```powershell
npm start          # Inicia servidor de desarrollo
npm run build      # Construye para producción
```

### Backend
```powershell
python manage.py runserver        # Inicia servidor
python manage.py migrate          # Ejecuta migraciones
```

## Configuración CORS

El backend está configurado para aceptar peticiones desde:
- `http://localhost:4200` (desarrollo)

Para modificar, editar `CORS_ALLOWED_ORIGINS` en `settings.py`.

## Base de Datos

El sistema utiliza MySQL con codificación UTF-8 (utf8mb4) para soporte completo de caracteres especiales.

### Migraciones Aplicadas
1. **0001_initial**: Estructura base
2. **0002_administradores**: Modelo de administradores
3. **0003_alumnos_maestros**: Modelos de alumnos y maestros
4. **0004_materias**: Modelo de materias

---

**Versión:** 0.0.0  
**Última actualización:** Diciembre 2025