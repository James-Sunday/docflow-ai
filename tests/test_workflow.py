from app.main import DocumentRequest, DocumentType, process


def request(**changes):
    values = {
        "document_type": DocumentType.INVOICE,
        "filename": "invoice-001.pdf",
        "vendor_id": "V-100",
        "invoice_number": "INV-001",
        "subtotal": 100,
        "tax": 7.5,
        "total": 107.5,
        "currency": "USD",
        "approved_vendor": True,
        "purchase_order_exists": True,
    }
    return DocumentRequest(**(values | changes))


def test_valid_invoice_is_ready_for_human_approval():
    result = process(request())
    assert result.status == "ready_for_human_approval"
    assert result.requires_review is False
    assert result.fields["total"].source_document == "invoice-001.pdf"


def test_business_rules_are_deterministic():
    result = process(request(total=99, approved_vendor=False, purchase_order_exists=False))
    assert result.validations == [
        "subtotal_plus_tax_must_equal_total",
        "vendor_must_be_approved",
        "purchase_order_must_exist",
    ]
    assert result.status == "review_required"
