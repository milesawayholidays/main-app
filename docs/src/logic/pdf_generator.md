# [`pdf_generator.py`](../../src/logic/pdf_generator.py)

This module generates a PDF document summarizing round-trip flight combinations and their details, including optional images and WhatsApp marketing text. It uses `fpdf` for layout and formatting.

---

## 📄 Overview

The `PDF` class extends `FPDF` to provide custom methods for rendering round-trip flight data. The `generate_pdf` function takes a `RoundTripOptions` object and compiles a summary document, suitable for sharing or archiving.

---

## 📦 Classes

### `PDF(FPDF)`

Custom subclass of `FPDF` used for structured travel report generation.

#### Methods

##### `header() -> None`

- Adds a centered title at the top of each page.

##### `add_round_trip(round_trip: RoundTrip, source: str) -> None`

- Adds a summary of a round-trip to the PDF:
  - Outbound and return flight information
  - Source of data
  - Normal selling price
  - Booking links
- Inserts spacing after each entry.

---

## 📦 Function

### `generate_pdf(roundTripOption: RoundTripOptions, title: str) -> PDF_OBJ`

Generates a PDF document based on flight options and marketing content.

#### Parameters:
- `roundTripOption` (`RoundTripOptions`): Contains round trip details, booking links, WhatsApp post, and images.
- `title` (`str`): Title of the PDF document.

#### Returns:
- `PDF_OBJ`: The generated PDF encoded as a UTF-8 byte string.

#### Behavior:
- Adds a title page with a list of round-trip combos.
- Includes WhatsApp post content using `multi_cell`.
- Appends images (if available), one per page.
- Uses `fpdf` for PDF formatting and layout.

---

## 🖼️ Image Support

- Each image in `roundTripOption.images` must implement:
  - `.buffer`: A `BytesIO` or similar stream used by `fpdf.image()`.

---

## 🔗 Dependencies

- [`fpdf`](https://py-pdf.github.io/fpdf2/): PDF rendering engine.
- [`logic.trip_builder`](../logic/trip_builder.md): Contains `RoundTripOptions` and `RoundTrip` definitions.
- [`data_types.pdf_types`](../data_types/pdf_types.md): Defines the `PDF_OBJ` return type.

---

## 🧠 Notes

- The layout is fixed-width, single-column, and center-aligned.
- Designed to support both human-readable summaries and WhatsApp-based promotional posts.
- Generates output entirely in memory—no files are written to disk.

---
