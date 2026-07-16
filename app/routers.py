from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud import add_note, create_ticket, delete_ticket, get_ticket_by_id, get_tickets, update_ticket_status
from app.database import get_db
from app.schemas import TicketCreate, TicketUpdate

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", include_in_schema=False)
def index(request: Request, db: Session = Depends(get_db), search: str = "", status: str = ""):
    try:
        tickets = get_tickets(db, search=search or None, status=status or None)
    except SQLAlchemyError:
        tickets = []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tickets": tickets,
            "search": search,
            "status": status,
        },
    )


@router.get("/tickets/new", include_in_schema=False)
def create_ticket_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@router.post("/tickets/new")
def handle_create_ticket(
    _request: Request,
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    ticket_data = {
        "customer_name": customer_name,
        "customer_email": customer_email,
        "subject": subject,
        "description": description,
    }

    try:
        create_ticket(db, ticket_data)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    return RedirectResponse(url="/", status_code=303)


@router.get("/tickets/{ticket_id}", include_in_schema=False)
def ticket_details(request: Request, ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return templates.TemplateResponse("details.html", {"request": request, "ticket": ticket})


@router.post("/tickets/{ticket_id}/status")
def update_status(ticket_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        update_ticket_status(db, ticket, status)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)


@router.post("/tickets/{ticket_id}/notes")
def add_ticket_note(ticket_id: int, note: str = Form(...), db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        add_note(db, ticket, note)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)


@router.post("/tickets/{ticket_id}/delete")
def delete_ticket_page(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        delete_ticket(db, ticket)
    except SQLAlchemyError:
        return HTMLResponse("Database connection failed. Please check your MySQL setup.", status_code=500)

    return RedirectResponse(url="/", status_code=303)


@router.post("/api/tickets", response_model=dict)
def create_api_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    try:
        created_ticket = create_ticket(db, ticket_data.model_dump())
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database connection failed") from exc

    return {"message": "Ticket created successfully", "ticket_id": created_ticket.ticket_id}


@router.get("/api/tickets", response_model=list[dict])
def list_api_tickets(db: Session = Depends(get_db), search: str = "", status: str = ""):
    try:
        tickets = get_tickets(db, search=search or None, status=status or None)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database connection failed") from exc

    return [
        {
            "id": ticket.id,
            "ticket_id": ticket.ticket_id,
            "customer_name": ticket.customer_name,
            "customer_email": ticket.customer_email,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status,
            "created_at": str(ticket.created_at),
            "updated_at": str(ticket.updated_at),
        }
        for ticket in tickets
    ]


@router.get("/api/tickets/{ticket_id}", response_model=dict)
def get_api_ticket(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database connection failed") from exc

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "id": ticket.id,
        "ticket_id": ticket.ticket_id,
        "customer_name": ticket.customer_name,
        "customer_email": ticket.customer_email,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "created_at": str(ticket.created_at),
        "updated_at": str(ticket.updated_at),
        "notes": [{"id": note.id, "note": note.note, "created_at": str(note.created_at)} for note in ticket.notes],
    }


@router.put("/api/tickets/{ticket_id}", response_model=dict)
def update_api_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database connection failed") from exc

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    updated_ticket = update_ticket_status(db, ticket, ticket_update.status)
    return {"message": "Ticket updated successfully", "status": updated_ticket.status}


@router.delete("/api/tickets/{ticket_id}", response_model=dict)
def delete_api_ticket(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = get_ticket_by_id(db, ticket_id)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database connection failed") from exc

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    delete_ticket(db, ticket)
    return {"message": "Ticket deleted successfully"}