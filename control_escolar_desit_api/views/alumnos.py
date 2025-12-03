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

class AlumnosAll(generics.CreateAPIView):
    #Verificar si el usuario esta autenticado
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        
        return Response(lista, 200)
    
class AlumnosView(generics.CreateAPIView):
    # CAMBIO: Permitir POST sin autenticación, requiere autenticación para el resto
    def get_permissions(self):
        if self.request.method == 'POST':
            # No requiere autenticación para registro
            return []
        # Requiere autenticación para otras operaciones (GET, PUT, DELETE)
        return [permissions.IsAuthenticated()]
    
    # Obtener alumno por ID
    def get(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        alumno_data = AlumnoSerializer(alumno, many=False).data
        
        # Aplanar datos del usuario para el frontend
        if "user" in alumno_data and alumno_data["user"]:
            alumno_data["first_name"] = alumno_data["user"].get("first_name", "")
            alumno_data["last_name"] = alumno_data["user"].get("last_name", "")
            alumno_data["email"] = alumno_data["user"].get("email", "")
        
        return Response(alumno_data, 200)
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
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
            user.save()

            #Create a profile for the user
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con ID: ": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos del alumno
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Obtener alumno
        alumno = get_object_or_404(Alumnos, id=request.data["id"])
        alumno.matricula = request.data["matricula"]
        alumno.curp = request.data["curp"].upper()
        alumno.rfc = request.data["rfc"].upper()
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.edad = request.data["edad"]
        alumno.telefono = request.data["telefono"]
        alumno.ocupacion = request.data["ocupacion"]
        alumno.save()
        
        # Actualizar datos del usuario 
        user = alumno.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        return Response({"message": "Alumno actualizado correctamente", "alumno": AlumnoSerializer(alumno).data}, 200)
    
    # Eliminar alumno
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        # Obtenemos alumno
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        # usuario
        user = alumno.user
        # Marcamos el usuario como inactivo (soft delete)
        user.is_active = 0
        user.save()
        # Eliminamos el alumno
        alumno.delete()
        
        return Response({"message": "Alumno eliminado correctamente"}, 200)