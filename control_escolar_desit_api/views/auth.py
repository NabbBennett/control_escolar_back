from django.db.models import *
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        print("=" * 50)
        print("INICIO DE LOGIN")
        print("=" * 50)
        
        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        print(f"Usuario: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Active: {user.is_active}")
        
        if user.is_active:
            # Obtener perfil y roles del usuario
            roles = user.groups.all()
            print(f"Grupos del usuario: {[r.name for r in roles]}")
            
            role_names = []
            # Verifico si el usuario tiene un perfil asociado
            for role in roles:
                role_names.append(role.name)

            if not role_names:
                print("ERROR: Usuario sin grupos asignados")
                return Response({"details":"Usuario sin rol asignado"}, 403)

            #Si solo es un rol especifico asignamos el elemento 0
            role_names = role_names[0].lower()  # Convertir a minúsculas
            print(f"Rol seleccionado: '{role_names}'")
            
            #Esta función genera la clave dinámica (token) para iniciar sesión
            token, created = Token.objects.get_or_create(user=user)
            print(f"Token generado: {token.key}")
            
           #Verificar que tipo de usuario quiere iniciar sesión
            
            if role_names == 'alumno':
                print("Buscando perfil de alumno...")
                alumno = Alumnos.objects.filter(user=user).first()
                if not alumno:
                    print("ERROR: Perfil de alumno no encontrado")
                    return Response({"details":"Perfil de alumno no encontrado"}, 404)
                alumno = AlumnoSerializer(alumno).data
                alumno["token"] = token.key
                alumno["rol"] = "alumno"
                print("Login exitoso como alumno")
                return Response(alumno,200)
            elif role_names == 'maestro':
                print("Buscando perfil de maestro...")
                maestro = Maestros.objects.filter(user=user).first()
                print(f"Maestro encontrado: {maestro}")
                if not maestro:
                    print("ERROR: Perfil de maestro no encontrado")
                    return Response({"details":"Perfil de maestro no encontrado"}, 404)
                maestro = MaestroSerializer(maestro).data
                maestro["token"] = token.key
                maestro["rol"] = "maestro"
                print("Login exitoso como maestro")
                return Response(maestro,200)
            elif role_names == 'administrador':
                print("Login como administrador...")
                user_data = UserSerializer(user, many=False).data
                user_data['token'] = token.key
                user_data["rol"] = "administrador"
                print("Login exitoso como administrador")
                return Response(user_data,200)
            else:
                print(f"ERROR: Rol no reconocido '{role_names}'")
                return Response({"details":f"Rol no reconocido: {role_names}"},403)
        
        print("ERROR: Usuario inactivo")
        return Response({}, status=status.HTTP_403_FORBIDDEN) 


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        print("logout")
        user = request.user
        print(str(user))
        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()

            return Response({'logout':True})


        return Response({'logout': False})