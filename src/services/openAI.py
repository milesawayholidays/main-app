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
                           origin_city: str, 
                           origin_country: str,
                           destination_city: str,
                           destination_country: str,
                           departure_dates: list[str], 
                           return_dates: list[str], 
                           cabin: str, 
                           miles_cost: str,
                           taxes: str,
                           source: str,
                           selling_price: str,
                           remaining_seats: str,
                           booking_link: str) -> str:
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
            ...     origin_city="São Paulo",
            ...     origin_country="Brasil",
            ...     destination_city="Paris",
            ...     destination_country="França",
            ...     departure_dates=["2025-08-15", "2025-08-20"],
            ...     return_dates=["2025-08-25", "2025-08-30"],
            ...     cabin="Premium",
            ...     selling_price="R$ 3.500,00 (BRL)"
            ... )
            "🌟 OFERTA EXCLUSIVA - Paris te espera! ✈️..."

        """

        prompt = f"\
          Crie um único post para um grupo de alertas de viagens no Whatsapp. Seja bem enfático na urgência e \
          exclusividade da oferta e dê seu melhor para convencer o leitor a comprar. \n\
          \n\
          O post DEVE conter as seguintes informações escritas em uma formatação variada e fluida: \
          De: {origin_city} - {origin_country} \
          Para: {destination_city} - {destination_country} \
          Cabine: {cabin} \
          Datas de ida: {', '.join(str(departure_dates))} \
          Datas de volta: {', '.join(str(return_dates))} \
          Emissora: {source} \
          Custo: {miles_cost} + {taxes} \
          Valor comprando conosco: {selling_price} \
          Assentos disponíveis: {remaining_seats} \
          Link de Emissão: {booking_link} \
          \n\
          REGRAS: \
          1. PROIBIDO HASHTAGS \n\
          2. PROIBIDO CARACTERES QUE NÃO SÃO AMPLAMENTE ACEITOS POR PADRÕES DE USO COMUM OU QUE POSSAM ATRAPALHAR A LEITURA \n\
          3. DEVE TER ALGUNS EMOJIS PARA EXPRESSAR TONALIDADE \n\
          4. SE NÃO HOUVER DATAS DE VOLTA, ASSUMA QUE A VIAGEM É DE IDA SOMENTE E ADAPTE O TEXTO CONFORME. \
          5. COLOQUE AS INFORMAÇÕES LISTADAS DE FORMA CLARA E ORGÂNICA \
          6. OMITA QUALQUER INFORMAÇÃO QUE VOCÊ RECEBER VAZIA (Como data de volta ou taxas) \
          7. ALGUMAS INFORMAÇÕES PODEM SER CENSURADAS POR UM OPERADOR HUMANO, ENTÃO FAÇA MENÇÃO DE QUE HÁ UM GRUPO PREMIUM ONDE ESSAS INFORMAÇÕES EXISTEM \
          \n\
          Mantenha um tom profissional, mas amigável e acessível. Seja breve e direto, não ultrapasse 200 palavras. \
          \n\
          O post deve conter uma chamada para ação, como \"Entre em contato para mais informações!\""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.9
        )

        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            raise ValueError("Failed to generate WhatsApp post: No valid response from OpenAI API.")


# Create a singleton instance for use throughout the application
handler = OPENAI_Handler()