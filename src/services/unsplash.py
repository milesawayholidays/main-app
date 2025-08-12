"""
Unsplash API integration service for fetching travel-related images.

This module provides functionality to fetch high-quality travel images from
Unsplash's API for use in flight alert marketing materials. It handles API
authentication, image search, download, and processing to create Image objects
suitable for embedding in PDFs and other marketing content.

Key Features:
- Travel image search via Unsplash API
- Multiple image retrieval (up to 3 per query)
- Automatic image downloading and processing
- Content-type validation for image files
- Squarish orientation optimization for marketing layouts
- Error handling for API failures and invalid responses

The module integrates with:
- Unsplash API for image search and retrieval
- Configuration management for API credentials
- Image data types for consistent object handling
- BytesIO for efficient binary data processing

Usage Context:
- Flight alert PDF generation
- WhatsApp post visual content
- Marketing material enhancement
- Destination-specific imagery for promotions
"""

import requests
from io import BytesIO

from config import config

from data_types.images import Image


def fetch_image(query: str) -> list[Image]:
    """
    Fetch travel-related images from Unsplash API based on search query.
    
    Searches Unsplash for images matching the provided query (typically
    destination cities or tourism attractions) and downloads up to 3
    high-quality images suitable for marketing materials.
    
    Args:
        query (str): Search query for images (e.g., "Paris Tourism Attraction",
            "Tokyo Travel", "London Landmarks")
            
    Returns:
        list[Image]: List of Image objects containing downloaded image data
            with URLs and binary buffers. Each image is named sequentially
            (image1.jpg, image2.jpg, etc.)
            
    Raises:
        Exception: If API request fails, no images are found, or download fails
        
    Note:
        - Fetches 3 images per query for variety
        - Uses 'squarish' orientation for consistent layout
        - Downloads 'small' size images for optimal performance
        - Creates Image objects with BytesIO buffers for immediate use
        - Requires valid UNSPLASH_ACCESS_KEY in configuration
        
    Example:
        >>> images = fetch_image("Paris Tourism Attraction")
        >>> len(images)  # Should return up to 3 images
        3
        >>> images[0].url  # Original Unsplash URL
        'https://images.unsplash.com/photo-...'
    """
    api_key = config.UNSPLASH_ACCESS_KEY
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "page": 1,
        "per_page": 3,
        "orientation": "squarish",
    }
    headers = {
        "Authorization": f"Client-ID {api_key}"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching images: {response.status_code} - {response.text}")

    data = response.json()
    if 'results' not in data or not data['results']:
        raise Exception("No images found for the query.")
    image_urls = [result['urls']['small'] for result in data.get('results', [])]
    if not image_urls:
        raise Exception("No images found for the query.")

    # Need to have a unique name to avoid overwriting files
    return [Image(url, save_image_in_disk(f"{hash(url)}.jpg", bytes(download_image(url)))) for url in image_urls]


def download_image(url: str) -> bytes:
    """
    Download image binary data from a URL with validation.
    
    Downloads the actual image file from the provided URL and validates
    that the response contains valid image data. This function ensures
    that only legitimate image files are processed and downloaded.
    
    Args:
        url (str): Direct URL to the image file (typically from Unsplash)
        
    Returns:
        bytes: Binary image data ready for processing or storage
        
    Raises:
        Exception: If download fails, URL returns non-image content,
            or HTTP request encounters an error
            
    Note:
        - Validates Content-Type header to ensure image data
        - Returns raw binary data for maximum flexibility
        - Used internally by fetch_image() function
        - Handles various image formats (JPEG, PNG, WebP, etc.)
        - No size limits - downloads full image as provided by URL
        
    Example:
        >>> image_data = download_image("https://images.unsplash.com/photo-...")
        >>> len(image_data)  # Size in bytes
        245760
        >>> type(image_data)
        <class 'bytes'>
    """
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Error downloading image: {response.status_code} - {response.text}")
    
    content_type = response.headers.get('Content-Type', '')
    if not content_type.startswith('image/'):
        raise Exception(f"URL did not return an image: Content-Type = {content_type}")
    
    return response.content

DEFAULT_FOLDER = "images"
def save_image_in_disk(filename: str, image_data: bytes) -> str:
    """
    Save image binary data to disk as a file.

    Args:
        filename (str): The local file path where the image should be saved
        image_data (bytes): The binary data of the image to be saved

    Returns:
        str: The full path to the saved image file

    Raises:
        IOError: If file writing fails due to permissions or other issues

    Note:
        - Uses binary write mode ('wb') to ensure correct file format
        - No validation on filename - assumes valid path provided

    Example:
        >>> img_data = fetch_image("Paris Tourism Attraction")[0].buffer
        >>> save_image_in_disk("paris_attraction.jpg", img_data)
    """

    import os
    if not os.path.exists(DEFAULT_FOLDER):
        os.makedirs(DEFAULT_FOLDER)

    with open(os.path.join(DEFAULT_FOLDER, filename), 'wb') as f:
        f.write(image_data)
    
    return DEFAULT_FOLDER + "/" + filename
        