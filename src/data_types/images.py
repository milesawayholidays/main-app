"""
Image data structures for handling travel-related images.

This module defines data structures used to represent images fetched
from external services (like Unsplash) for use in flight alerts and
promotional materials. These objects encapsulate both the image
metadata and binary data for processing and embedding.
"""

from dataclasses import dataclass
from io import BytesIO

@dataclass
class Image:
    """
    Represents an image with its URL and binary data.
    
    This data structure is used to encapsulate images fetched from
    external services (primarily Unsplash) for use in flight alerts,
    WhatsApp posts, and PDF reports. It contains both the original
    URL for reference and the downloaded binary data for processing.
    
    Attributes:
        url (str): The original URL of the image from the external service
        buffer (bytes): The binary data of the downloaded image file
    """
    url: str
    filePath: str