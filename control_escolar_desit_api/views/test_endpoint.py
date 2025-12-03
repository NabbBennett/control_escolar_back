from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class TestEndpoint(APIView):
    """
    Endpoint de prueba para verificar CORS y recepción de datos
    """
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        print("=" * 50)
        print("TEST ENDPOINT - Datos recibidos:")
        print("Headers:", dict(request.headers))
        print("Data:", request.data)
        print("=" * 50)
        
        return Response({
            "status": "success",
            "message": "Test endpoint funcionando correctamente",
            "received_data": request.data,
            "headers": dict(request.headers)
        }, status=200)
    
    def get(self, request, *args, **kwargs):
        return Response({
            "status": "success",
            "message": "Test endpoint GET funcionando"
        }, status=200)
