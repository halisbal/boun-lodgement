from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Lodgement
from .serializers import LodgementSerializer


class LodgementListView(APIView):
    def get(self, request):
        lodgements = Lodgement.objects.all()
        serializer = LodgementSerializer(lodgements, many=True)
        return Response(serializer.data)
