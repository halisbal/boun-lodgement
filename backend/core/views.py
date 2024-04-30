from datetime import datetime

import boto3
from django.core.files.base import ContentFile
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from src.settings import AWS_STORAGE_BUCKET_NAME
from .constants import (
    ApplicationStatus,
    FormType,
    SIRA_TAHSIS_4_NOLU_CETVEL_FORM,
    FormItemTypes,
)
from .models import (
    Lodgement,
    Queue,
    Application,
    Form,
    FormItem,
    ApplicationDocument,
    Document,
)
from .serializers import LodgementSerializer, ApplicationSerializer, QueueSerializer


class LodgementListView(APIView):
    def get(self, request):
        lodgements = Lodgement.objects.all()
        serializer = LodgementSerializer(lodgements, many=True)
        return Response(serializer.data)


class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Queue.objects.filter(personel_type=user.type)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"error": "Queue not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().get(pk=kwargs.get("pk"))
        except Application.DoesNotExist:
            return Response(
                {"error": "Queue not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def apply(self, request, *args, **kwargs):
        user = request.user
        queue_id = kwargs.get("pk")

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

        applications = Application.objects.filter(
            user=user,
            queue=queue,
        ).exclude(status__in=[ApplicationStatus.CANCELLED, ApplicationStatus.REJECTED])
        if applications.exists():
            return JsonResponse(
                {"error": "You already have an active application for this queue"},
                status=status.HTTP_400_BAD_REQUEST,
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

    @action(detail=True, methods=["GET"], url_path="submit-documents/presigned-url")
    def get_presigned_url(self, request, pk=None):
        application = self.get_object()

        if application.status in [
            ApplicationStatus.REJECTED,
            ApplicationStatus.CANCELLED,
        ]:
            return Response(
                {
                    "error": "Cannot submit document for an application that is not active."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document_id = request.query_params.get("document_id")
        if not document_id:
            return Response(
                {"error": "Document ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        document = Document.objects.filter(id=document_id).first()
        if not document:
            return Response(
                {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
            )

        s3 = boto3.client("s3")
        bucket_name = AWS_STORAGE_BUCKET_NAME
        file_name = (
            f"{request.user.email}-{document.name}-{datetime.now().isoformat()}"
        )
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": file_name},
            ExpiresIn=3600,
        )

        return Response({"url": presigned_url})

    @action(detail=True, methods=["POST"], url_path="submit-documents")
    def submit_documents(self, request, pk=None):
        application = self.get_object()

        if application.status in [
            ApplicationStatus.REJECTED,
            ApplicationStatus.CANCELLED,
        ]:
            return Response(
                {
                    "error": "Cannot submit document for an application that is not active."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data

        if not isinstance(data, list):
            return Response(
                {"error": "Invalid data format, expected a list of items"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not data:
            return Response(
                {"error": "Document is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        s3 = boto3.client("s3")
        bucket_name = AWS_STORAGE_BUCKET_NAME

        for obj in data:
            document_id = obj.get("document_id")
            document = Document.objects.filter(id=document_id).first()
            if not document:
                return Response(
                    {"error": f"Document with ID {document_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            description = obj.get("description")
            file = obj.get("file")
            response = s3.get_object(Bucket=bucket_name, Key=file)
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                return Response(
                    {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
                )
            file_content = response["Body"].read()
            django_file = ContentFile(file_content, name=file.split("/")[-1])

            ApplicationDocument.objects.create(
                document=document,
                application=application,
                description=description,
                file=django_file,
            )

        application = self.get_object()
        serializer = self.get_serializer(application)
        return Response(serializer.data)
