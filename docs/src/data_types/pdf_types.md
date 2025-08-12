# [`pdf_obj.py`](../../src/data_types/pdf_types.py)

This module defines a simple dataclass for representing a PDF document in memory, typically used for file attachments, local storage, or email communication.

## Classes

### `PDF_OBJ`
A lightweight data structure that encapsulates the title and binary content of a generated PDF.

#### Fields:
- `title: str`  
  A string representing the filename or display name of the PDF. Used for labeling or saving the file.

- `bin: bytes`  
  The binary content of the PDF file. This is the actual encoded document, suitable for writing to disk or attaching to an email.

This structure simplifies the interface for handling generated PDFs by bundling both metadata and content.
