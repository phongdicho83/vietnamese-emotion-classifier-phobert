# Vietnamese Emotion Classifier

Web application for classifying emotions in Vietnamese text using PhoBERT base v2 with sentiment analysis pipeline and Vietnamese dictionary enhancement.

## Features

- Classifies Vietnamese text into: POSITIVE, NEUTRAL, NEGATIVE
- Hybrid approach: Pre-trained sentiment model + Vietnamese dictionary
- Supports Vietnamese without diacritics (không dấu)
- Recognizes common Vietnamese abbreviations and slang
- Test button with 10 sample sentences
- Browser localStorage for classification history (last 50 records)
- History view with timestamps
- Docker containerization for easy deployment
- Clean, responsive web interface
- Real-time emotion classification

## Installation

**Quick Start (Windows):**

```bash
start.bat
```

**Quick Start (Linux/Mac):**

```bash
chmod +x start.sh
./start.sh
```

**Manual Installation:**

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

3. Open your browser and go to: `http://localhost:5000`

## Usage

1. Enter Vietnamese text and click "Phân loại cảm xúc" to classify
2. Click "Kiểm tra 10 câu mẫu" to test with 10 sample sentences
3. Click "Xem lịch sử phân loại" to view classification history

## Classification Method

Advanced hybrid approach using PhoBERT:

1. **PhoBERT Base v2 Model**

   - Uses `vinai/phobert-base-v2` - state-of-the-art Vietnamese language model
   - Attempts to load fine-tuned sentiment model `wonrax/phobert-base-vietnamese-sentiment`
   - Falls back to base PhoBERT with custom classification head if needed
   - Proper Vietnamese word segmentation and tokenization

2. **Vietnamese Text Preprocessing**

   - Expands abbreviations (k→không, dc→được, mk→mình, etc.)
   - Normalizes text without diacritics
   - Handles 80+ common Vietnamese slang terms

3. **Sentiment Dictionary Analysis**

   - 50+ positive words (tốt, hay, đẹp, vui, thích, etc.)
   - 50+ negative words (tệ, xấu, dở, buồn, ghét, etc.)
   - Negation handling (không, chẳng, chả)
   - Intensifier detection (rất, cực, quá, lắm)

4. **Smart Hybrid Classification**
   - Strong dictionary signals (2+ sentiment words) → Trust dictionary
   - Weak dictionary signal → Trust PhoBERT model
   - Medium signal → Combine both for best accuracy
   - Fallback to dictionary-only if model fails

This PhoBERT-based approach provides superior accuracy for Vietnamese text, especially for:

- Complex sentence structures
- Context-dependent sentiment
- Slang and abbreviations
- Text without diacritics

## Storage

The application uses browser localStorage to store classification history:

- Stores last 50 classification results
- Data persists in browser (cleared if browser data is cleared)
- No server-side database required
- Lightweight and fast

**API Endpoints:**

- `POST /classify` - Classify text and return result

## Architecture

For detailed system architecture, data flow, and component diagrams, see [ARCHITECTURE.md](ARCHITECTURE.md)
