# [`images.py`](../../src/data_types/images.py)

This module defines a simple dataclass for representing an image object used throughout the system, particularly in PDF generation or external API integrations like Unsplash.

## Classes

### `Image`
A lightweight data structure to represent an image with both a reference URL and its binary content.

#### Fields:
- `url: str`  
  A string representing the source URL of the image. This may point to an external service or CDN.

- `buffer: bytes`  
  The raw byte content of the image, typically used for in-memory operations such as rendering into PDFs or sending as attachments.

This structure abstracts the dual nature of images in the app — being both externally sourced and internally used.
