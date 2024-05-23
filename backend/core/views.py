from datetime import datetime

import boto3
import pytz
from django.core.files.base import ContentFile
from django.db.models import Min
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
    days_until,
)
from .models import (
    Lodgement,
    Queue,
    Application,
    Form,
    FormItem,
    ApplicationDocument,
    Document,
    ScoringFormItem,
    ScoringFormLog,
)
from .serializers import (
    LodgementSerializer,
    ApplicationSerializer,
    QueueSerializer,
    ScoringFormItemSerializer,
)


class LodgementListView(APIView):
    def get(self, request):
        lodgements = Lodgement.objects.all()
        serializer = LodgementSerializer(lodgements, many=True)
        return Response(serializer.data)


class ScoringFormViewSet(viewsets.ModelViewSet):
    queryset = ScoringFormItem.objects.all()
    serializer_class = ScoringFormItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScoringFormItem.objects.filter(type=FormType.SCORING)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"error": "Scoring form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def get_latest(self, request, *args, **kwargs):
        user = request.user
        log = ScoringFormLog.objects.filter(user=user).last()
        if not log:
            return Response([])
        data = log.data
        return Response(data)


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

        log = ScoringFormLog.objects.filter(user=user).last()
        data = log.data if log else []
        for item in data:
            item["label"] = (
                ScoringFormItem.objects.filter(id=item.get("scoring_form_item_id"))
                .first()
                .label
            )

        for item in SIRA_TAHSIS_4_NOLU_CETVEL_FORM:
            answer = None
            for item_data in data:
                if item_data["label"] == item["label"]:
                    answer = item_data["answer"]
                    break
            form.items.create(
                label=item["label"],
                caption=item["caption"],
                field_type=item["field_type"],
                point=item["point"],
                answer={"value": answer},
            )

        serializer = ApplicationSerializer(application)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def evaluate(self, request, *args, **kwargs):
        user = request.user
        form_data = request.data

        queue_id = kwargs.get("pk")
        queue = Queue.objects.filter(id=queue_id).first()

        if not isinstance(form_data, list):
            return Response(
                {"error": "Invalid data format, expected a list of items"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_points = 0
        for item in form_data:
            scoring_form_item_id = item.get("scoring_form_item_id")
            answer = item.get("answer")

            if scoring_form_item_id is None or answer is None:
                continue

            scoring_form_item = ScoringFormItem.objects.filter(
                id=scoring_form_item_id
            ).first()
            if not scoring_form_item:
                continue

            if scoring_form_item.field_type == FormItemTypes.INTEGER:
                if not isinstance(answer, int):
                    return Response(
                        {"error": "Invalid data type for an answer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif scoring_form_item.field_type == FormItemTypes.BOOLEAN:
                if not isinstance(answer, int):
                    return Response(
                        {"error": "Invalid data type for an answer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            total_points += scoring_form_item.point * answer

        ScoringFormLog.objects.create(user=user, data=form_data)

        applications = queue.applications.filter(
            status__in=[ApplicationStatus.APPROVED],
        )

        current_rank = 1
        for application in applications:
            if application.scoring_form.total_points > total_points:
                current_rank += 1

        if queue.lodgements.count() == 0:
            approximate_availability = None
        else:
            new_application = Application(user=user, queue=queue, id=-1)
            pq = queue.get_priority_queue(
                new_application=new_application, new_application_points=total_points
            )
            approximate_availability = list(
                filter(lambda x: x.get("application").id == -1, pq)
            )[0].get("estimated_availability_date")

        return Response(
            {
                "total_points": total_points,
                "rank": current_rank,
                "approximate_availability": days_until(approximate_availability),
            }
        )


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

        log_data = []

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

                if ScoringFormItem.objects.filter(label=form_item.label).exists():
                    log_data.append(
                        {
                            "scoring_form_item_id": ScoringFormItem.objects.filter(
                                label=form_item.label
                            )
                            .first()
                            .id,
                            "answer": answer,
                        }
                    )
                form_item.answer = {"value": answer}
                form_item.save()

            if log_data:
                ScoringFormLog.objects.create(user=request.user, data=log_data)
            serializer = self.get_serializer(application)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"], url_path="submit-documents/presigned-url")
    def get_presigned_url(self, request, pk=None):
        application = self.get_object()
        file_format = request.query_params.get("file_format")

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
        from botocore.client import Config

        s3 = boto3.client(
            "s3",
            region_name="eu-central-1",
            config=Config(signature_version="s3v4"),
        )
        bucket_name = AWS_STORAGE_BUCKET_NAME
        file_name = f"default/application_documents/{request.user.email}-{document.name}-{datetime.now().isoformat()}.{file_format}"
        presigned_url = s3.generate_presigned_post(
            Bucket=bucket_name,
            Key=file_name,
            Fields=None,
            Conditions=None,
            ExpiresIn=3600,
        )

        return Response(presigned_url)

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

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        application = self.get_object()

        if application.status not in [
            ApplicationStatus.IN_PROGRESS,
            ApplicationStatus.PENDING,
            ApplicationStatus.RE_UPLOAD,
        ]:
            return Response(
                {"error": "Application status is not suitable for this operation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = ApplicationStatus.CANCELLED
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def send_to_approve(self, request, pk=None):
        application = self.get_object()

        if application.status not in [
            ApplicationStatus.IN_PROGRESS,
            ApplicationStatus.RE_UPLOAD,
        ]:
            return Response(
                {"error": "Application status is not suitable for this operation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = ApplicationStatus.PENDING
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def cancel_approval(self, request, pk=None):
        application = self.get_object()

        if application.status != ApplicationStatus.PENDING:
            return Response(
                {"error": "Application status is not suitable for this operation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = ApplicationStatus.IN_PROGRESS
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)
