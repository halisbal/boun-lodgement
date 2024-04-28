from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .constants import (
    ApplicationStatus,
    FormType,
    SIRA_TAHSIS_4_NOLU_CETVEL_FORM,
    FormItemTypes,
)
from .models import Lodgement, Queue, Application, Form, FormItem
from .serializers import LodgementSerializer, ApplicationSerializer


class LodgementListView(APIView):
    def get(self, request):
        lodgements = Lodgement.objects.all()
        serializer = LodgementSerializer(lodgements, many=True)
        return Response(serializer.data)


class ApplyQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        queue_id = request.data.get("queue_id")

        if not queue_id:
            return JsonResponse(
                {"error": "Queue ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return JsonResponse(
                {"error": "Queue not found"}, status=status.HTTP_404_NOT_FOUND
            )

        application = Application.objects.create(
            user=user, status=ApplicationStatus.IN_PROGRESS, queue=queue
        )

        form = Form.objects.create(type=FormType.SCORING, application=application)

        for item in SIRA_TAHSIS_4_NOLU_CETVEL_FORM:
            form.items.create(
                label=item["label"],
                caption=item["caption"],
                field_type=item["field_type"],
                point=item["point"],
            )

        serializer = ApplicationSerializer(application)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Application.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().get(pk=kwargs.get("pk"))
        except Application.DoesNotExist:
            return Response(
                {"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        application = self.get_object()

        if application.status in [
            ApplicationStatus.APPROVED,
            ApplicationStatus.REJECTED,
        ]:
            return Response(
                {"error": "Cannot cancel an application that is already finalized."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = ApplicationStatus.CANCELLED
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], url_path="submit-scoring-form")
    def submit_scoring_form(self, request, pk=None):
        application = self.get_object()
        scoring_form = application.scoring_form

        if not scoring_form:
            return Response(
                {"error": "Scoring form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        form_data = request.data

        if not isinstance(form_data, list):
            return Response(
                {"error": "Invalid data format, expected a list of items"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            for item in form_data:
                form_item_id = item.get("form_item_id")
                answer = item.get("answer")

                if form_item_id is None or answer is None:
                    continue

                form_item = FormItem.objects.filter(
                    id=form_item_id, form=scoring_form
                ).first()
                if not form_item:
                    continue

                if form_item.field_type == FormItemTypes.INTEGER:
                    if not isinstance(answer, int):
                        return Response(
                            {"error": "Invalid data type for an answer"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                elif form_item.field_type == FormItemTypes.BOOLEAN:
                    if not isinstance(answer, int):
                        return Response(
                            {"error": "Invalid data type for an answer"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                elif form_item.field_type == FormItemTypes.TEXT:
                    if not isinstance(answer, str):
                        if not isinstance(answer, int):
                            return Response(
                                {"error": "Invalid data type for an answer"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                form_item.answer = {"value": answer}
                form_item.save()

            serializer = self.get_serializer(application)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
