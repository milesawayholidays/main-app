# [`openAI.py`](../../src/services/openAI.py)

This module defines the `OPENAI_Handler` class which interfaces with OpenAI's API to generate compelling WhatsApp posts for travel alert promotions. It creates persuasive, professional marketing content tailored for flight deal alerts in Portuguese, designed to drive engagement and conversions in WhatsApp group communications.

---

## 📄 Overview

The `OPENAI_Handler` class provides automated WhatsApp post generation using OpenAI's GPT models. It follows the application's deferred initialization pattern, requiring explicit `load()` call with API key before use.

The handler specializes in creating Portuguese marketing content that:
- Emphasizes urgency and exclusivity for conversion optimization
- Maintains professional yet accessible tone
- Includes accessibility-friendly formatting (no hashtags or problematic characters)
- Integrates flight details and pricing seamlessly
- Provides call-to-action for customer engagement
- Offers negotiation options for one-way trips

---

## 📦 Classes

### `OPENAI_Handler`

Handles communication with OpenAI API for travel marketing content generation.

#### Initialization (`__init__(self)`)

Creates an uninitialized handler instance. No API client is created until `load()` is called.

#### Methods

##### `load(self, api_key: str) -> None`

Initializes the OpenAI client with the provided API key.

- **Parameters:**
  - `api_key` (`str`): OpenAI API key for authentication
- **Behavior:**
  - Creates authenticated OpenAI client instance
  - No validation performed - errors occur on first API call if key is invalid
  - Should be called before any content generation methods

##### `generateWhatsAppPost(self, origin: str, destination: str, departure_dates: list[str], return_dates: list[str], cabin: str, selling_price: str) -> str`

Generates a compelling WhatsApp post for flight deal promotion.

- **Parameters:**
  - `origin` (`str`): Origin location in format "City(Country)"
  - `destination` (`str`): Destination location in format "City(Country)"
  - `departure_dates` (`list[str]`): List of available departure dates
  - `return_dates` (`list[str]`): List of available return dates
  - `cabin` (`str`): Cabin class identifier (e.g., 'Y', 'W')
  - `selling_price` (`str`): Formatted selling price with currency symbol

- **Returns:**
  - `str`: Generated WhatsApp post content in Portuguese, optimized for engagement and conversion

- **Behavior:**
  - Parses origin/destination strings to extract city and country components
  - Constructs detailed Portuguese prompt with marketing instructions
  - Uses GPT-4o model with temperature 0.7 for creative content
  - Limits response to 300 tokens for optimal WhatsApp readability
  - Creates urgency-focused content with professional emojis
  - Includes negotiation option for one-way trips
  - Maintains accessibility by avoiding hashtags and problematic characters

- **Raises:**
  - `ValueError`: If OpenAI API fails to generate valid response

- **Content Guidelines:**
  - Maximum 200 words for optimal readability
  - Professional but friendly and accessible tone
  - Emphasis on urgency and exclusivity
  - Include call-to-action phrase
  - Professional emoji usage (not excessive)
  - Accessibility-friendly formatting

---

## 🏗️ Singleton Pattern

The module creates a singleton instance for application-wide use:

```python
handler = OPENAI_Handler()
```

This instance should be loaded once during application startup using `handler.load(api_key)`.

---

## 🧠 Error Handling

- **API Response Validation**: Raises `ValueError` if OpenAI API fails to generate valid response
- **Input Processing**: Gracefully parses origin/destination strings to extract city and country
- **Token Management**: Uses max_tokens=300 to ensure reasonable response length
- **Content Validation**: Ensures response exists and contains message content before returning

---

## � Usage Examples

### Basic Usage

```python
from services.openAI import handler as openai_handler

# Initialize the handler (typically done during app startup)
openai_handler.load(api_key="your_openai_api_key_here")

# Generate WhatsApp post for a flight deal
post_content = openai_handler.generateWhatsAppPost(
    origin="São Paulo(Brazil)",
    destination="Paris(France)",
    departure_dates=["2025-08-15", "2025-08-20"],
    return_dates=["2025-08-25", "2025-08-30"],
    cabin="W",
    selling_price="R$ 3.500,00 (BRL)"
)

print(post_content)
```

### Integration with Flight Processing

```python
# Typical usage in flight alert pipeline
def create_marketing_content(trip_option) -> str:
    """Generate marketing post for a trip option"""
    try:
        return openai_handler.generateWhatsAppPost(
            origin=f"{trip_option.origin_city}({trip_option.origin_country})",
            destination=f"{trip_option.destination_city}({trip_option.destination_country})",
            departure_dates=trip_option.departure_dates,
            return_dates=trip_option.return_dates,
            cabin=trip_option.cabin,
            selling_price=trip_option.formatted_price
        )
    except ValueError as e:
        state.logger.error(f"Failed to generate WhatsApp post: {e}")
        return "Oferta especial de viagem disponível! Entre em contato para detalhes."
```

### Handling API Failures

```python
def safe_post_generation(trip_details) -> str:
    """Generate post with fallback for API failures"""
    try:
        return openai_handler.generateWhatsAppPost(**trip_details)
    except ValueError:
        # Fallback to template-based content
        return generate_template_post(trip_details)
    except Exception as e:
        state.logger.error(f"Unexpected error in post generation: {e}")
        raise
```

---

## 🎯 Content Strategy

**Marketing Approach:**
- **Urgency**: Emphasizes limited-time availability and exclusivity
- **Trust Building**: Professional tone with accessible language
- **Accessibility**: No hashtags or characters that interfere with screen readers
- **Negotiation**: Mentions flexibility for one-way trip arrangements
- **Engagement**: Clear call-to-action for immediate response

**Format Optimization:**
- Maximum 200 words for WhatsApp readability
- Professional emoji usage for visual appeal
- Clear information hierarchy with flight details
- Brazilian Portuguese language and cultural context
- Mobile-first formatting considerations

---

## 🔐 Authentication

**API Key Requirements:**
- Valid OpenAI API key with GPT-4o model access
- Sufficient credit balance for API usage
- API key passed directly to `load()` method (not from config)

**Model Configuration:**
- **Model**: GPT-4o for high-quality content generation
- **Temperature**: 0.7 for creative but consistent output
- **Max Tokens**: 300 to ensure concise messaging
- **Response Format**: Text completion for marketing content

---

## 🔗 Dependencies

- [`openai`](https://pypi.org/project/openai/): Official OpenAI Python client library for API access
- [`config`](../config.md): Configuration management (imported but API key passed directly)

---

## ⚠️ Notes

- **Deferred Loading**: Handler requires explicit `load()` call with API key
- **Language Specialization**: Optimized specifically for Brazilian Portuguese content
- **Token Management**: Uses token limits to control response length and API costs
- **Content Guidelines**: Follows strict accessibility and professional standards
- **No Config Dependency**: API key is passed directly rather than loaded from configuration
- **Marketing Focus**: Designed specifically for WhatsApp group travel promotions
