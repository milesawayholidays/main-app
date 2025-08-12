# [`unsplash.py`](../../src/services/unsplash.py)

This module provides functionality to search for and download travel-related images from the Unsplash API. It's designed for fetching high-quality destination imagery for use in flight alert marketing materials, PDFs, and promotional content.

---

## 📄 Overview

The module implements a function-based approach for image retrieval from Unsplash's comprehensive photography database. It specializes in travel and tourism imagery, providing automatic image downloading and processing for immediate use in marketing materials.

Key capabilities:
- **Travel Image Search**: Query-based search for destination and tourism images
- **Multi-Image Retrieval**: Downloads up to 3 images per query for variety
- **Automatic Processing**: Handles download, validation, and Image object creation
- **Marketing Optimization**: Prioritizes squarish orientation for consistent layouts
- **Content Validation**: Ensures downloaded content is valid image data
- **Immediate Use**: Returns ready-to-use Image objects with BytesIO buffers

---

## 📦 Functions

### `fetch_image(query: str) -> list[Image]`

Fetches travel-related images from Unsplash API based on search query.

#### Parameters:
- **`query`** (`str`): Search query for images. Best results with destination-focused terms like:
  - "Paris Tourism Attraction"
  - "Tokyo Travel"
  - "London Landmarks"
  - "Brazil Destination"

#### Returns:
- **`list[Image]`**: List of Image objects containing:
  - `url`: Original Unsplash image URL
  - `buffer`: BytesIO stream with binary image data
  - Sequential naming: image1.jpg, image2.jpg, image3.jpg

#### Behavior:
- **API Query**: Searches Unsplash with specified parameters:
  - `per_page`: 3 images for variety
  - `orientation`: "squarish" for consistent layout
  - `page`: 1 (first page of results)
- **Image Processing**: Downloads 'small' size images for optimal performance
- **Object Creation**: Creates Image objects with BytesIO buffers for immediate use
- **Error Handling**: Comprehensive validation of API responses and image downloads

#### Raises:
- **`Exception`**: If API request fails, no images found, or download errors occur

#### Usage Examples:
```python
from services.unsplash import fetch_image

# Fetch destination images
paris_images = fetch_image("Paris Tourism Attraction")
print(f"Downloaded {len(paris_images)} Paris images")

# Use in PDF generation
for image in paris_images:
    print(f"Image URL: {image.url}")
    print(f"Data size: {len(image.buffer.getvalue())} bytes")
```

### `download_image(url: str) -> bytes`

Downloads image binary data from a URL with comprehensive validation.

#### Parameters:
- **`url`** (`str`): Direct URL to the image file (typically from Unsplash)

#### Returns:
- **`bytes`**: Raw binary image data ready for processing or storage

#### Behavior:
- **HTTP Request**: Downloads image content with error handling
- **Content Validation**: Verifies Content-Type header indicates image data
- **Format Support**: Handles JPEG, PNG, WebP, and other image formats
- **Error Detection**: Validates successful download and content type

#### Raises:
- **`Exception`**: If download fails, URL returns non-image content, or HTTP errors occur

#### Usage Examples:
```python
from services.unsplash import download_image

# Download specific image
image_data = download_image("https://images.unsplash.com/photo-...")
print(f"Downloaded {len(image_data)} bytes")

# Validate content type
if len(image_data) > 0:
    print("Image downloaded successfully")
```

---

## 🧠 Error Handling

- **API Response Validation**: Checks HTTP status codes and response structure
- **Content Verification**: Validates that URLs return actual image data
- **Empty Results**: Raises exceptions when no images match the search query
- **Network Failures**: Handles connection errors and timeouts gracefully
- **Content-Type Validation**: Ensures downloaded content is valid image format

---

## 💡 Usage Examples

### Basic Image Fetching

```python
from services.unsplash import fetch_image

# Fetch images for a destination
destination = "Tokyo"
images = fetch_image(f"{destination} Tourism Attraction")

for i, image in enumerate(images, 1):
    print(f"Image {i}: {image.url}")
    with open(f"tokyo_{i}.jpg", "wb") as f:
        f.write(image.buffer.getvalue())
```

### Integration with PDF Generation

```python
from services.unsplash import fetch_image
from logic.pdf_generator import add_images_to_pdf

def create_destination_pdf(destination_city):
    """Create PDF with destination images"""
    try:
        # Fetch destination images
        images = fetch_image(f"{destination_city} Tourism Attraction")
        
        # Use images in PDF generation
        pdf_content = add_images_to_pdf(images)
        return pdf_content
        
    except Exception as e:
        print(f"Failed to fetch images for {destination_city}: {e}")
        return create_pdf_without_images()
```

### Marketing Content Pipeline

```python
from services.unsplash import fetch_image

def enhance_marketing_content(destination):
    """Add visual content to marketing materials"""
    try:
        # Fetch multiple image options
        tourism_images = fetch_image(f"{destination} Tourism")
        landmark_images = fetch_image(f"{destination} Landmarks")
        
        # Combine and select best images
        all_images = tourism_images + landmark_images
        selected_images = all_images[:3]  # Use top 3
        
        return selected_images
        
    except Exception as e:
        print(f"Image fetching failed: {e}")
        return []  # Fallback to no images
```

### Error Handling Pattern

```python
from services.unsplash import fetch_image

def safe_image_fetch(query, fallback_query=None):
    """Fetch images with fallback options"""
    try:
        return fetch_image(query)
    except Exception as e:
        print(f"Primary query failed: {e}")
        
        if fallback_query:
            try:
                return fetch_image(fallback_query)
            except Exception as e2:
                print(f"Fallback query failed: {e2}")
        
        return []  # No images available

# Usage with fallbacks
images = safe_image_fetch(
    "Paris Eiffel Tower",
    fallback_query="Paris Tourism"
)
```

---

## 🎨 Image Specifications

**API Parameters:**
- **Orientation**: "squarish" for consistent marketing layouts
- **Size**: "small" for optimal performance (400px on the smaller side)
- **Count**: 3 images per query for variety
- **Quality**: High-quality photographs from professional contributors

**Search Optimization:**
- Use specific destination names for better results
- Include tourism/travel keywords for relevant imagery
- Avoid generic terms for more targeted results
- Consider cultural landmarks and attractions in queries

**File Handling:**
- Images returned as BytesIO objects for immediate use
- No temporary file creation required
- Binary data ready for PDF embedding or file writing
- Sequential naming convention for organization

---

## 🔐 Authentication

**Unsplash API Requirements:**
- Valid Unsplash developer account
- Application registered with Unsplash
- Access key with appropriate rate limits

**Configuration:**
- **`config.UNSPLASH_ACCESS_KEY`**: Client-ID for API authentication
- Header format: `Authorization: Client-ID {access_key}`

**Rate Limits:**
- Enforced by Unsplash API (typically 50 requests/hour for free tier)
- No client-side throttling implemented
- Monitor usage to avoid quota exhaustion

---

## 🔗 Dependencies

- [`requests`](https://docs.python-requests.org/): HTTP client for API communication and image downloads
- [`io.BytesIO`](https://docs.python.org/3/library/io.html): In-memory binary stream handling
- [`config`](../config.md): Configuration management for API credentials
- [`Image`](../data_types/images.md): Data structure for image object handling

---

## ⚠️ Notes

- **No Caching**: Images are fetched fresh on each request
- **Network Dependent**: Requires active internet connection for all operations
- **API Quotas**: Monitor usage to avoid rate limit exhaustion
- **Image Quality**: Downloads 'small' size for performance (can be adjusted)
- **Content Rights**: Unsplash images have specific licensing terms
- **Error Resilience**: Functions raise exceptions rather than failing silently
- **Memory Usage**: Images loaded into memory as BytesIO objects
