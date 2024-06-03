from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import Lodgement, ScoringFormItem, Queue, Application
from .constants import (
    FormType,
    LodgementSizes,
    FormItemTypes,
    LodgementType,
    LodgementSize,
    ApplicationStatus,
)
from constants import UserRoles, PersonalType

User = get_user_model()


class LodgementViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.manager_user = User.objects.create(
            username="manager",
            email="manager@example.com",
            password="managerpassword",
            role=UserRoles.MANAGER,
        )
        self.regular_user = User.objects.create(
            username="regularuser",
            email="user@example.com",
            password="userpassword",
            role=UserRoles.USER,
        )
        self.token = Token.objects.create(user=self.manager_user)
        self.queue = Queue.objects.create(
            lodgement_type=LodgementType.SEQUENTIAL_ALLOCATION,
            personel_type=PersonalType.ACADEMIC,
            lodgement_size=LodgementSize.ONE_PLUS_ONE,
        )
        self.lodgement = Lodgement.objects.create(
            name="Test Lodgement",
            size=LodgementSizes.ONE_PLUS_ONE,
            description="A test lodgement",
            location="Test Location",
            is_available=True,
            queue=self.queue,
        )
        self.lodgement_url = reverse("core:lodgement-list")

    def test_list_lodgements(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.lodgement_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lodgement_as_non_manager(self):
        non_manager_token = Token.objects.create(user=self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + non_manager_token.key)
        lodgement_data = {
            "name": "New Lodgement",
            "size": LodgementSizes.ONE_PLUS_ONE,
            "description": "New lodgement description",
            "location": "New Location",
            "is_available": True,
        }
        response = self.client.post(self.lodgement_url, lodgement_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lodgement_as_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        update_url = reverse("core:lodgement-detail", args=[self.lodgement.id])
        update_data = {"name": "Updated Name"}
        response = self.client.patch(update_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lodgement.refresh_from_db()
        self.assertEqual(self.lodgement.name, "Updated Name")


class ScoringFormViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.token = Token.objects.create(user=self.user)
        self.scoring_form_item = ScoringFormItem.objects.create(
            type=FormType.SCORING,
            label="Test Label",
            caption="Test Caption",
            field_type=FormItemTypes.INTEGER,
            point=10,
        )
        self.scoring_form_url = reverse("core:scoringformitem-list")

    def test_list_scoring_form_items(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.scoring_form_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)


class QueueViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", role=UserRoles.MANAGER
        )
        self.queue = Queue.objects.create(
            lodgement_type=LodgementType.SERVICE_ALLOCATION,
            personel_type=PersonalType.ACADEMIC,
            lodgement_size=1,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_queues(self):
        response = self.client.get(reverse("core:queue-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_queues_not_found(self):
        Queue.objects.all().delete()
        response = self.client.get(reverse("core:queue-list"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Queue not found")

    def test_retrieve_queue(self):
        response = self.client.get(
            reverse("core:queue-detail", kwargs={"pk": self.queue.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.queue.id)

    def test_evaluate_queue_invalid_data_format(self):
        evaluate_url = reverse("core:queue-evaluate", kwargs={"pk": self.queue.id})
        form_data = {"invalid": "data"}
        response = self.client.post(evaluate_url, form_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Invalid data format, expected a list of items"
        )
