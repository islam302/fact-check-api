# Testing Image Fact Check API

## Prerequisites

1. **Install dependencies** (if not already installed):
   ```bash
   pip install Pillow requests
   ```

2. **Set up environment variables** in `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPAPI_KEY=your_serpapi_key_here  # Optional, for source verification
   ```

3. **Make sure Django server is running**:
   ```bash
   python manage.py runserver
   ```

## Testing Methods

### Method 1: Using the Test Script

```bash
# Basic usage
python image_fact_check/test_image_check.py path/to/image.jpg

# With language parameter
python image_fact_check/test_image_check.py path/to/image.jpg --lang ar

# With custom URL
python image_fact_check/test_image_check.py path/to/image.jpg --url http://localhost:8000
```

### Method 2: Using cURL

```bash
# Basic request
curl -X POST http://localhost:8000/image_check/ \
  -F "image=@path/to/image.jpg"

# With language parameter
curl -X POST http://localhost:8000/image_check/?lang=en \
  -F "image=@path/to/image.jpg"

# Save response to file
curl -X POST http://localhost:8000/image_check/ \
  -F "image=@path/to/image.jpg" \
  -o response.json
```

### Method 3: Using Python requests

```python
import requests

url = "http://localhost:8000/image_check/"
files = {'image': open('image.jpg', 'rb')}
params = {'lang': 'en'}  # Optional

response = requests.post(url, files=files, params=params)
print(response.json())
```

### Method 4: Using Postman or Thunder Client

1. **Method**: POST
2. **URL**: `http://localhost:8000/image_check/`
3. **Body Type**: `form-data`
4. **Fields**:
   - Key: `image` (type: File)
   - Value: Select your image file
   - Key: `lang` (type: Text, optional)
   - Value: `en`, `ar`, `fr`, etc.

### Method 5: Using HTTPie

```bash
# Install HTTPie: pip install httpie

http --form POST http://localhost:8000/image_check/ \
  image@path/to/image.jpg \
  lang==en
```

## Expected Response

```json
{
  "ok": true,
  "is_ai_generated": false,
  "ai_confidence": 0.15,
  "ai_indicators": ["Natural lighting patterns", "Realistic shadows"],
  "fact_check": {
    "case": "True",
    "talk": "The image shows...",
    "extracted_text": "Text found in image",
    "claims": ["Claim 1", "Claim 2"],
    "sources": [
      {
        "title": "Source Title",
        "url": "https://example.com",
        "snippet": "Relevant snippet..."
      }
    ]
  },
  "image_analysis": {
    "description": "Detailed description of image",
    "context": "Context information",
    "notable_elements": ["Element 1", "Element 2"]
  },
  "manipulation_signs": [],
  "language": "en"
}
```

## Test Cases

### 1. Test with a Real Photo
```bash
python image_fact_check/test_image_check.py test_images/real_photo.jpg
```
Expected: `is_ai_generated: false`, low confidence score

### 2. Test with an AI-Generated Image
```bash
python image_fact_check/test_image_check.py test_images/ai_generated.jpg
```
Expected: `is_ai_generated: true`, higher confidence score

### 3. Test with Arabic Text in Image
```bash
python image_fact_check/test_image_check.py test_images/arabic_text.jpg --lang ar
```
Expected: Language detected as 'ar', Arabic responses

### 4. Test Error Handling (Invalid File)
```bash
curl -X POST http://localhost:8000/image_check/ \
  -F "image=@not_an_image.txt"
```
Expected: 400 error with message about invalid file type

### 5. Test Error Handling (Missing File)
```bash
curl -X POST http://localhost:8000/image_check/
```
Expected: 400 error with message about missing image

## Common Issues

### Connection Error
- **Problem**: Cannot connect to server
- **Solution**: Make sure Django server is running on `http://localhost:8000`

### Invalid API Key Error
- **Problem**: OpenAI API key error
- **Solution**: Check your `.env` file has `OPENAI_API_KEY` set correctly

### File Too Large
- **Problem**: Image exceeds 10MB limit
- **Solution**: Resize or compress the image before uploading

### CORS Error (if testing from browser)
- **Problem**: CORS policy blocking request
- **Solution**: Ensure the origin is in `CORS_ALLOWED_ORIGINS` in `settings.py`

## Creating Test Images

You can create test images or download sample images:

1. **Real Photos**: Use any photo from your device or download from Unsplash
2. **AI-Generated**: Use DALL-E, Midjourney, or Stable Diffusion to generate test images
3. **Images with Text**: Create images with claims/statements using any image editor

## Quick Test Commands

```bash
# Test with sample image (if you have one)
python image_fact_check/test_image_check.py sample.jpg

# Test with Arabic language
python image_fact_check/test_image_check.py sample.jpg --lang ar

# Test API health (should return error for missing image)
curl http://localhost:8000/image_check/
```

