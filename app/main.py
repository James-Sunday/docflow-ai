from enum import StrEnum

from fastapi import FastAPI
from pydantic import BaseModel, Field


class DocumentType(StrEnum):
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    VENDOR_FORM = "vendor_onboarding_form"
    EXPENSE = "expense_document"
    CONTRACT = "contract"


class SourceField(BaseModel):
    value: str | float
    confidence: float = Field(ge=0, le=1)
    source_document: str
    source_page: int = Field(ge=1)
    evidence_text: str
    extraction_method: str = "deterministic_mock"


class DocumentRequest(BaseModel):
    document_type: DocumentType
    filename: str = Field(min_length=3, pattern=r"^[^/\\]+$")
    vendor_id: str
    invoice_number: str
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0)
    total: float = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    approved_vendor: bool
    purchase_order_exists: bool


class DocumentResult(BaseModel):
    document_type: DocumentType
    fields: dict[str, SourceField]
    validations: list[str]
    requires_review: bool
    status: str


def process(request: DocumentRequest) -> DocumentResult:
    validations: list[str] = []
    if abs((request.subtotal + request.tax) - request.total) > 0.01:
        validations.append("subtotal_plus_tax_must_equal_total")
    if not request.approved_vendor:
        validations.append("vendor_must_be_approved")
    if not request.purchase_order_exists:
        validations.append("purchase_order_must_exist")
    fields = {
        name: SourceField(
            value=value,
            confidence=1,
            source_document=request.filename,
            source_page=1,
            evidence_text=f"Synthetic input field: {name}",
        )
        for name, value in {
            "vendor_id": request.vendor_id,
            "invoice_number": request.invoice_number,
            "subtotal": request.subtotal,
            "tax": request.tax,
            "total": request.total,
            "currency": request.currency,
        }.items()
    }
    return DocumentResult(
        document_type=request.document_type,
        fields=fields,
        validations=validations,
        requires_review=bool(validations),
        status="review_required" if validations else "ready_for_human_approval",
    )


app = FastAPI(title="DocFlow AI", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "extractor": "deterministic_mock"}


@app.post("/api/v1/documents/process", response_model=DocumentResult)
def process_document(request: DocumentRequest) -> DocumentResult:
    return process(request)
