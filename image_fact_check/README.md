# Image Fact Check App

This Django app provides image fact-checking and AI-generation detection functionality using OpenAI's Vision API.

## Features

- **AI Generation Detection**: Determines if an image is AI-generated with confidence scoring
- **Content Fact-Checking**: Verifies claims and information visible in images
- **Image Analysis**: Provides detailed description of image content
- **Multi-language Support**: Supports Arabic, English, French, Spanish, and more
- **Source Verification**: Searches for sources to verify claims found in images

## API Endpoint

### POST `/image_check/`

Upload an image for fact-checking and AI-generation detection.

#### Request

- **Method**: POST
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `image` (required): Image file (JPEG, PNG, GIF, WebP)
  - `lang` (optional): Language hint (ar, en, fr, es, etc.)

#### Response

```json
{
  "ok": true,
  "is_ai_generated": boolean,
  "ai_confidence": float (0.0-1.0),
  "ai_indicators": ["list of AI detection signs"],
  "fact_check": {
    "case": "حقيقي/غير مؤكد/مزيف" or "True/Uncertain/False",
    "talk": "Detailed explanation",
    "extracted_text": "Any text visible in image",
    "claims": ["list of claims"],
    "sources": [{"title": "...", "url": "...", "snippet": "..."}]
  },
  "image_analysis": {
    "description": "Comprehensive description",
    "context": "Context information",
    "notable_elements": ["list of elements"]
  },
  "manipulation_signs": ["signs of editing"],
  "language": "detected language code"
}
```

## Example Usage

### Using cURL

```bash
curl -X POST http://localhost:8000/image_check/ \
  -F "image=@path/to/image.jpg" \
  -F "lang=en"
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/image_check/"
files = {'image': open('image.jpg', 'rb')}
params = {'lang': 'en'}

response = requests.post(url, files=files, params=params)
print(response.json())
```

## Requirements

- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)
- SerpAPI key (optional, for source verification - set as `SERPAPI_KEY`)
- Pillow library for image processing

## File Structure

```
image_fact_check/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── utils.py          # Image analysis utilities
├── views.py          # API endpoint views
└── urls.py           # URL routing
```

