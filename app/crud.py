import uuid

from sqlalchemy.orm import Session

from app.models import Note, Ticket


def create_ticket(db: Session, ticket_data: dict):
    ticket = Ticket(
        ticket_id=str(uuid.uuid4())[:8].upper(),
        customer_name=ticket_data["customer_name"],
        customer_email=ticket_data["customer_email"],
        subject=ticket_data["subject"],
        description=ticket_data["description"],
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_tickets(db: Session, search=None, status=None):
    query = db.query(Ticket)

    if search:
        search_value = f"%{search}%"
        query = query.filter(
            (Ticket.ticket_id.like(search_value))
            | (Ticket.customer_name.like(search_value))
            | (Ticket.subject.like(search_value))
            | (Ticket.customer_email.like(search_value))
        )

    if status:
        query = query.filter(Ticket.status == status)

    return query.order_by(Ticket.created_at.desc()).all()


def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update_ticket_status(db: Session, ticket: Ticket, status: str):
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket


def add_note(db: Session, ticket: Ticket, note_text: str):
    note = Note(ticket_id=ticket.id, note=note_text)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def delete_ticket(db: Session, ticket: Ticket):
    db.delete(ticket)
    db.commit()