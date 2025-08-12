"""
PDF data structures for document generation and handling.

This module defines data structures used to represent PDF documents
and their metadata throughout the flight alert system. These objects
are used to pass PDF data between generation, storage, and delivery
components.
"""

from dataclasses import dataclass


@dataclass
class PDF_OBJ:
    """
    Represents a PDF document with its metadata and binary data.
    
    This data structure is used to encapsulate PDF documents generated
    by the system, including flight alert reports and trip summaries.
    It contains both the document title/filename and the actual PDF
    binary data for processing and delivery.
    
    Attributes:
        title (str): The title/filename of the PDF document
        filePath (str): The file path where the PDF is stored
    """
    title: str
    filePath: str