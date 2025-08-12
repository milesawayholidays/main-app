"""
OpenAI service for generating WhatsApp travel alert posts.

This module integrates with OpenAI's API to generate compelling WhatsApp posts
for flight alert promotions. It creates persuasive, professional marketing
content tailored for travel deal alerts in Portuguese, designed to drive
engagement and conversions in WhatsApp group communications.

Key Features:
- Automated WhatsApp post generation via OpenAI GPT models
- Portuguese language marketing content creation
- Professional yet accessible tone optimization
- Accessibility-friendly formatting (no hashtags or problematic characters)
- Customizable flight details integration
- Urgency and exclusivity emphasis for conversion optimization

The module generates posts that include:
- Origin and destination information
- Flight dates and cabin class details
- Pricing information and selling points
- Call-to-action for customer engagement
- Professional emojis for visual appeal
- Negotiation options for one-way trips
"""

from openai import OpenAI

from config import config


class OPENAI_Handler:
    """
    Handler class for OpenAI API operations focused on travel marketing content.
    
    This class manages OpenAI API interactions specifically for generating
    WhatsApp marketing posts for flight alerts. It handles API authentication,
    prompt engineering, and response processing to create compelling travel
    marketing content.
    
    Attributes:
        client (OpenAI): Authenticated OpenAI API client instance
        
    Note:
        - Requires valid OpenAI API key in configuration
        - Optimized for Portuguese language content generation
        - Designed for WhatsApp group marketing contexts
    """
    
    def __init__(self):
        pass

    def load(self, api_key):
        """
        Load OpenAI API key for authentication.
        
        This method initializes the OpenAI client with the provided API key,
        allowing subsequent calls to the OpenAI API for content generation.
        
        Args:
            api_key (str): The OpenAI API key for authentication
            
        Note:
            - Should be called before any content generation methods
            - No validation - errors will occur on first API call if key is invalid
        """
        self.client = OpenAI(api_key=api_key)

    def generateWhatsAppPost(self,
                           origin: str, 
                           destination: str, 
                           departure_dates: list[str], 
                           return_dates: list[str], 
                           cabin: str, 
                           selling_price: str) -> str:
        """
        Generate a compelling WhatsApp post for flight deal promotion.
        
        Creates a persuasive marketing post in Portuguese for WhatsApp groups,
        designed to promote flight deals with urgency and exclusivity. The post
        includes all flight details, pricing, and a strong call-to-action while
        maintaining accessibility and professional presentation.
        
        Args:
            origin (str): Origin location (format: "City(Country)")
            destination (str): Destination location (format: "City(Country)")
            departure_dates (list[str]): List of available departure dates
            return_dates (list[str]): List of available return dates
            cabin (str): Cabin class identifier (e.g., 'Y', 'W')
            selling_price (str): Formatted selling price with currency
            
        Returns:
            str: Generated WhatsApp post content in Portuguese, optimized for
                engagement and conversion, limited to 200 words
                
        Raises:
            ValueError: If OpenAI API fails to generate a valid response
            
        Note:
            - Content is in Portuguese for Brazilian market
            - Includes professional emojis (not excessive)
            - Avoids hashtags and accessibility-problematic characters
            - Emphasizes urgency and exclusivity for conversion
            - Includes negotiation option for one-way trips
            - Maintains professional but friendly tone
            - Limited to 200 words for optimal WhatsApp readability
            
        Example:
            >>> handler.generateWhatsAppPost(
            ...     origin="São Paulo(Brazil)",
            ...     destination="Paris(France)", 
            ...     departure_dates=["2025-08-15", "2025-08-20"],
            ...     return_dates=["2025-08-25", "2025-08-30"],
            ...     cabin="W",
            ...     selling_price="R$ 3.500,00 (BRL)"
            ... )
            "🌟 OFERTA EXCLUSIVA - Paris te espera! ✈️..."
        """
        # Parse origin and destination to extract city and country
        origin_parts = origin.split('(')
        origin_city = origin_parts[0]
        origin_country = origin_parts[1].rstrip(')') if len(origin_parts) > 1 else ''
        
        destination_parts = destination.split('(')
        destination_city = destination_parts[0]
        destination_country = destination_parts[1].rstrip(')') if len(destination_parts) > 1 else ''

        prompt = f"\
          Crie um post para um grupo de alertas de viagens no Whatsapp. Seja bem enfático na urgência e \
          exclusividade da oferta e dê seu melhor para convencer o leitor a comprar. \
          Adicionalmente, avise que caso o leitor tenha interesse apenas em uma viagem de ida, que estamos a disposição para negociar.\
          O nome da nossa empresa é 'MilesAway Holidays'. \
          \n\
          Observação: Se houver apenas uma data de ida e nenhuma de volta, o post deve ser adaptado para uma viagem de ida, mantendo o tom de urgência e exclusividade.\
          \n\
          O post deve conter as seguintes informações (não necessáriamente nesta formatação): \
          Origem: {origin_city} - {origin_country} \
          Destino: {destination_city} - {destination_country} \
          Cabine: {cabin} \
          Datas de ida: {', '.join(departure_dates)} \
          Datas de volta: {', '.join(return_dates)} \
          Valor de venda: {selling_price} \
          \n\
          O post deve conter emojis, só não exager. Também não coloque hashtags ou outros caracteres que possam atrapalhar a leitura para deficientes visuais e demais \
          \n\
          Matenha um tom profissional, mas amigável e acessível. Seja breve e direto, não ultrapasse 200 palavras. \
          \n\
          O post deve conter uma chamada para ação, como \"Entre em contato para mais informações!\""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            raise ValueError("Failed to generate WhatsApp post: No valid response from OpenAI API.")


# Create a singleton instance for use throughout the application
handler = OPENAI_Handler()