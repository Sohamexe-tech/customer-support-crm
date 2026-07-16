from pydantic import BaseModel, EmailStr, Field


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=150)
    customer_email: EmailStr
    subject: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)


class TicketUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)


class NoteCreate(BaseModel):
    note: str = Field(..., min_length=1)


class TicketOut(BaseModel):
    id: int
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class NoteOut(BaseModel):
    id: int
    ticket_id: int
    note: str
    created_at: str

    class Config:
        from_attributes = True
