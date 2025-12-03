from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import UserSerializer
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

class AdminAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    #Obtener usuario por ID requiere autenticación
    def get_permissions(self):
        if self.request.method == 'POST':
            # No requiere autenticación para registro
            return []
        # Requiere autenticación para otras operaciones (GET, PUT, DELETE)
        return [permissions.IsAuthenticated()]
    
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin_data = AdminSerializer(admin, many=False).data
        
        # Aplanar datos del usuario para el frontend
        if "user" in admin_data and admin_data["user"]:
            admin_data["first_name"] = admin_data["user"].get("first_name", "")
            admin_data["last_name"] = admin_data["user"].get("last_name", "")
            admin_data["email"] = admin_data["user"].get("email", "")
        
        # Si todo es correcto, regresamos la información
        return Response(admin_data, 200)
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Serializamos los datos del administrador para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            #Grabar datos del administrador
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            group.save()

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"Admin creado con el ID: ": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos del administrador
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        try:
            # administrador a actualizar
            admin = get_object_or_404(Administradores, id=request.data.get("id"))
            
            # Actualizar campos del administrador 
            if "clave_admin" in request.data:
                admin.clave_admin = request.data["clave_admin"]
            elif "numero_trabajador" in request.data:
                admin.clave_admin = request.data["numero_trabajador"]
            if "telefono" in request.data:
                admin.telefono = request.data["telefono"]
            if "rfc" in request.data:
                admin.rfc = request.data["rfc"].upper()
            if "edad" in request.data:
                admin.edad = request.data["edad"]
            if "ocupacion" in request.data:
                admin.ocupacion = request.data["ocupacion"]
            
            admin.save()
            
            # Actualizamos los datos 
            user = admin.user
            if "first_name" in request.data:
                user.first_name = request.data["first_name"]
            if "last_name" in request.data:
                user.last_name = request.data["last_name"]
            user.save()
            
            return Response({"message": "Administrador actualizado correctamente", "admin": AdminSerializer(admin).data}, 200)
        except Exception as e:
            return Response({"message": "Error al actualizar administrador", "error": str(e)}, 500)

    
    # Eliminar administrador
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        # Obtenemos el administrador
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        # Obtenemos el usuario 
        user = admin.user
        # Marcamos el usuario como inactivo (soft delete)
        user.is_active = 0
        user.save()
        # Eliminamos 
        admin.delete()
        
        return Response({"message": "Administrador eliminado correctamente"}, 200)
       
class TotalUsers(generics.CreateAPIView):
    #Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        # TOTAL ADMINISTRADORES
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        # TOTAL MAESTROS
        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestroSerializer(maestros_qs, many=True).data

        # Convertir materias_json solo si existen maestros
        for maestro in lista_maestros:
            try:
                maestro["materias_json"] = json.loads(maestro["materias_json"])
            except Exception:
                maestro["materias_json"] = []  # fallback seguro

        total_maestros = maestros_qs.count()

        # TOTAL ALUMNOS
        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        # Respuesta final SIEMPRE válida
        return Response(
            {
                "admins": total_admins,
                "maestros": total_maestros,
                "alumnos": total_alumnos
            },
            status=200
        )
