
"""
PDF generation functionality for flight alerts and reports.

This module provides functionality to generate PDF documents containing
flight alert information, including round trip details, pricing, booking
links, WhatsApp posts, and travel images. It extends the FPDF library
to create formatted reports for email distribution and archival purposes.

The module includes:
- Custom PDF class with header formatting
- Round trip information formatting
- Image embedding for travel visuals
- WhatsApp post content integration
"""

from fpdf import FPDF

from global_state import state

from logic.trip_builder import RoundTripOptions, RoundTrip

from data_types.pdf_types import PDF_OBJ

DEFAULT_FOLDER = "pdfs"

class PDF(FPDF):
    """
    Custom PDF class extending FPDF for flight alert reports.
    
    This class provides specialized methods for generating flight alert
    PDFs with consistent formatting, headers, and content organization.
    It handles the layout and presentation of round trip information,
    pricing details, and associated images.
    """
    
    def header(self):
        """
        Add a header to each page of the PDF.
        
        Creates a centered title header using the PDF's title property
        with bold formatting and appropriate spacing.
        """
        # Use Arial/Helvetica for compatibility
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, self.title, 0, 1, "C")
        self.ln(5)

    def add_round_trip(self, round_trip: RoundTrip, source):
        """
        Add round trip information to the PDF.
        
        Formats and adds complete round trip details including outbound
        and return flight information, source, pricing, and booking links
        to the current page position.
        
        Args:
            round_trip (RoundTrip): The round trip object containing
                outbound and return flight details
            source: The airline source/program for the trip
            
        Note:
            - Adds flight departure times and airport codes
            - Includes selling price in cents
            - Provides booking links for both flights
            - Adds spacing after the trip information
        """
        state.logger.info(f"Adding round trip: {round_trip.outbound.origin_airport} to {round_trip.outbound.destination_airport}")
        self.set_font("Arial", "", 12)
        normal_selling_price = round_trip.normal_selling_price_to_str()
        self.cell(0, 10, f"Outbound: {round_trip.outbound.departure} - {round_trip.outbound.origin_airport} to {round_trip.outbound.destination_airport}", 0, 1)
        self.cell(0, 10, f"Return: {round_trip.return_.departure} - {round_trip.return_.origin_airport} to {round_trip.return_.destination_airport}", 0, 1)
        self.cell(0, 10, f"Source: {source}", 0, 1)
        self.cell(0, 10, f"Selling Price: {normal_selling_price}", 0, 1)

        # Use multi_cell for booking links with better text handling
        # Break long URLs into smaller chunks if needed
        outbound_links = round_trip.outbound.booking_links
        return_links = round_trip.return_.booking_links

        self.cell(0, 10, "Outbound Booking Links:", 0, 1)
        self.write(5, "\n".join(outbound_links))

        self.cell(0, 10, "Return Booking Links:", 0, 1)
        self.write(5, "\n".join(return_links))
        
        self.ln(5)
        return


def generate_pdf(roundTripOptions: RoundTripOptions, title: str) -> PDF_OBJ:
    """
    Generate a complete PDF report for flight alert round trip options.
    
    Creates a comprehensive PDF document containing all round trip information,
    WhatsApp post content, and associated travel images. The PDF includes:
    - Title page with round trip summary
    - Individual round trip details with pricing and booking links
    - WhatsApp post content for social media
    - Travel images on separate pages
    
    Args:
        roundTripOption (RoundTripOptions): Object containing all round trip
            data, WhatsApp post, and associated images
        title (str): Title for the PDF document and header
        
    Returns:
        PDF_OBJ: PDF object containing the title and binary PDF data
        
    Note:
        - Uses automatic page breaks with 15pt margin
        - Adds a main title "Top 15 Combos de Voos - Econômico"
        - Each image is placed on a separate page with their download link
        - WhatsApp post content is included as multi-line text
        - Returns PDF as binary data encoded in UTF-8
    """
    state.logger.info(f"Generating PDF for {title}")
    pdf = PDF()
    pdf.title = f"{title}"
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.cell(0, 10, f"top 5 voos {roundTripOptions.cabin} de {roundTripOptions.origin_city}-{roundTripOptions.origin_country} para {roundTripOptions.destination_city}-{roundTripOptions.destination_country}", 0, 1, "C")

    for round_trip in roundTripOptions.roundTrips:
        pdf.add_round_trip(round_trip, roundTripOptions.source)
        pdf.add_page()

    for image in roundTripOptions.images:
        state.logger.info(f"Adding image: {image.url}")
        pdf.add_page()
        pdf.cell(0, 10, f"url: {image.url}", 0, 1)
        pdf.cell(0, 10, f"", 0, 1)

        pdf.image(image.filePath, w=pdf.w - 20)
    
    import os
    if not os.path.exists(DEFAULT_FOLDER):
        os.makedirs(DEFAULT_FOLDER)

    filePath = os.path.join(DEFAULT_FOLDER, title.replace(" ", "_") + ".pdf")
    pdf.output(filePath)
    # Return PDF
    return PDF_OBJ(
        title=title,
        filePath=filePath
    )