import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api import create_api_router
from app.database import TicketNotFoundError, TicketRepository
from app.models import TicketCreate, TicketFilters, TicketPriority, TicketStatus, TicketUpdate


class TicketRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TicketRepository(":memory:")

    def tearDown(self) -> None:
        self.repository.close()

    @staticmethod
    def ticket(title: str, priority: TicketPriority = TicketPriority.medium) -> TicketCreate:
        return TicketCreate(
            title=title,
            description=f"Description for {title}",
            requester="Test User",
            priority=priority,
        )

    def test_seed_defaults_is_idempotent(self) -> None:
        self.repository.seed_defaults()
        self.repository.seed_defaults()
        self.assertEqual(3, len(self.repository.list()))

    def test_crud_preserves_mapping_and_exact_ids(self) -> None:
        first = self.repository.create(self.ticket("First ticket", TicketPriority.high))
        second = self.repository.create(self.ticket("Second ticket", TicketPriority.low))

        self.assertEqual(1, first.id)
        self.assertEqual(2, second.id)
        self.assertEqual(TicketPriority.high, first.priority)
        self.assertEqual(TicketStatus.open, first.status)
        self.assertEqual(second.id, self.repository.update(second.id, TicketUpdate()).id)

        updated = self.repository.update(first.id, TicketUpdate(status=TicketStatus.resolved))
        self.assertEqual(TicketStatus.resolved, updated.status)
        self.repository.delete(first.id)
        self.assertEqual(second.id, self.repository.get(second.id).id)
        with self.assertRaises(TicketNotFoundError):
            self.repository.get(first.id)

    def test_combined_filters_and_case_insensitive_partial_search(self) -> None:
        first = self.repository.create(self.ticket("VPN access", TicketPriority.high))
        self.repository.create(self.ticket("Printer toner", TicketPriority.low))
        self.repository.update(first.id, TicketUpdate(status=TicketStatus.in_progress))

        matches = self.repository.list(
            TicketFilters(
                status=TicketStatus.in_progress,
                priority=TicketPriority.high,
                search="vpn",
            )
        )
        self.assertEqual([first.id], [ticket.id for ticket in matches])
        self.assertEqual([], self.repository.list(TicketFilters(search="no such ticket")))

    def test_missing_update_and_delete_raise(self) -> None:
        with self.assertRaises(TicketNotFoundError):
            self.repository.update(999, TicketUpdate(status=TicketStatus.closed))
        with self.assertRaises(TicketNotFoundError):
            self.repository.delete(999)


class TicketValidationTests(unittest.TestCase):
    def test_create_rejects_empty_and_blank_fields(self) -> None:
        invalid_values = ("", "   ")
        for value in invalid_values:
            with self.subTest(value=repr(value)), self.assertRaises(ValidationError):
                TicketCreate(title=value, description="Valid description", requester="Valid User")

    def test_create_accepts_seed_sized_values_and_trims_input(self) -> None:
        ticket = TicketCreate(
            title="  Valid title  ",
            description="A description longer than twenty characters is valid.",
            requester="A requester name",
        )
        self.assertEqual("Valid title", ticket.title)

    def test_update_rejects_explicit_null_and_blank_values(self) -> None:
        with self.assertRaises(ValidationError):
            TicketUpdate(title=None)
        with self.assertRaises(ValidationError):
            TicketUpdate(title="   ")


class TicketApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TicketRepository(":memory:")
        app = FastAPI()
        app.include_router(create_api_router(self.repository))
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        self.repository.close()

    def create_ticket(self, title: str, priority: str = "medium") -> dict[str, object]:
        response = self.client.post(
            "/api/tickets",
            json={
                "title": title,
                "description": f"Description for {title}",
                "requester": "API User",
                "priority": priority,
            },
        )
        self.assertEqual(201, response.status_code)
        return response.json()

    def test_create_get_patch_and_delete_use_exact_id(self) -> None:
        first = self.create_ticket("First API ticket")
        second = self.create_ticket("Second API ticket")
        first_id = int(first["id"])
        second_id = int(second["id"])

        self.assertEqual(first, self.client.get(f"/api/tickets/{first_id}").json())
        patch = self.client.patch(f"/api/tickets/{second_id}", json={"status": "closed"})
        self.assertEqual(200, patch.status_code)
        self.assertEqual("closed", patch.json()["status"])
        self.assertEqual(204, self.client.delete(f"/api/tickets/{first_id}").status_code)
        self.assertEqual(200, self.client.get(f"/api/tickets/{second_id}").status_code)

    def test_filters_are_forwarded_and_can_be_combined(self) -> None:
        first = self.create_ticket("Network outage", "urgent")
        self.create_ticket("Mouse replacement", "low")
        first_id = int(first["id"])
        self.client.patch(f"/api/tickets/{first_id}", json={"status": "in_progress"})

        response = self.client.get(
            "/api/tickets",
            params={"status": "in_progress", "priority": "urgent", "search": "network"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual([first_id], [ticket["id"] for ticket in response.json()])
        self.assertEqual([], self.client.get("/api/tickets", params={"search": "missing"}).json())

    def test_not_found_invalid_id_and_invalid_body_statuses(self) -> None:
        missing = self.client.get("/api/tickets/999")
        self.assertEqual(404, missing.status_code)
        self.assertIn("Ticket 999 was not found", missing.json()["detail"])
        self.assertEqual(422, self.client.get("/api/tickets/0").status_code)
        self.assertEqual(422, self.client.patch("/api/tickets/1", json={"title": None}).status_code)
        self.assertEqual(
            422,
            self.client.post(
                "/api/tickets",
                json={"title": "", "description": "valid description", "requester": "API User"},
            ).status_code,
        )


if __name__ == "__main__":
    unittest.main()
