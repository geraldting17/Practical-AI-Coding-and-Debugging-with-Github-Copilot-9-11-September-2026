from app.database import TicketRepository
from app.models import TicketFilters, TicketPriority, TicketStatus
from app.ui import (
    _FILTER_PRIORITY_OPTIONS,
    _FILTER_STATUS_OPTIONS,
    _PRIORITY_OPTIONS,
    _STATUS_OPTIONS,
    _build_ticket_filters,
)


def test_list_query_keeps_parameter_order_and_sorting() -> None:
    query, parameters = TicketRepository._build_list_query(
        TicketFilters(
            status=TicketStatus.open,
            priority=TicketPriority.high,
            search="VPN",
        )
    )

    assert query == (
        "SELECT * FROM tickets WHERE status = ? AND priority = ? "
        "AND (title LIKE ? OR description LIKE ? OR requester LIKE ?) "
        "ORDER BY created_at ASC, id ASC"
    )
    assert parameters == ["open", "high", "%VPN%", "%VPN%", "%VPN%"]


def test_seed_data_remains_idempotent_and_ordered() -> None:
    repository = TicketRepository(":memory:")
    repository.seed_defaults()
    repository.seed_defaults()

    tickets = repository.list()

    assert [ticket.title for ticket in tickets] == [
        "Laptop cannot connect to VPN",
        "New finance dashboard access",
        "Broken conference room display",
    ]
    assert [ticket.priority for ticket in tickets] == [
        TicketPriority.high,
        TicketPriority.medium,
        TicketPriority.low,
    ]


def test_ui_filter_helper_keeps_existing_filter_values() -> None:
    assert _STATUS_OPTIONS == [status.value for status in TicketStatus]
    assert _PRIORITY_OPTIONS == [priority.value for priority in TicketPriority]
    assert _FILTER_STATUS_OPTIONS == ["all", *_STATUS_OPTIONS]
    assert _FILTER_PRIORITY_OPTIONS == ["all", *_PRIORITY_OPTIONS]

    filters = _build_ticket_filters("open", "high", "VPN")
    assert filters == TicketFilters(
        status=TicketStatus.open,
        priority=TicketPriority.high,
        search="VPN",
    )
    assert _build_ticket_filters("all", "all", "") == TicketFilters()
