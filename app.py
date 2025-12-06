from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from vietnamese_processor import VietnameseTextProcessor

app = Flask(__name__)

# Initialize Vietnamese text processor
text_processor = VietnameseTextProcessor()

# Load PhoBERT model and tokenizer
MODEL_NAME = "vinai/phobert-base-v2"
print(f"Loading {MODEL_NAME}...")

try:
    # Try to load a fine-tuned PhoBERT sentiment model if available
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Try to use pre-trained Vietnamese PhoBERT sentiment model
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            "wonrax/phobert-base-vietnamese-sentiment",
            num_labels=3
        )
        print("Using fine-tuned PhoBERT sentiment model (wonrax/phobert-base-vietnamese-sentiment)")
    except:
        # Create our own classification head on top of PhoBERT
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME,
            num_labels=3
        )
        print("Using PhoBERT base with custom classification head")
    
    model.eval()
    
    # Create sentiment pipeline
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=-1  # CPU
    )
    
except Exception as e:
    print(f"Error loading PhoBERT: {e}")
    print("Falling back to dictionary-only classification")
    sentiment_pipeline = None

# Emotion labels mapping
LABEL_MAPPING = {
    'LABEL_0': 'NEGATIVE',
    'LABEL_1': 'NEUTRAL', 
    'LABEL_2': 'POSITIVE',
    'NEG': 'NEGATIVE',
    'NEU': 'NEUTRAL',
    'POS': 'POSITIVE'
}

def classify_emotion(text):
    """Classify Vietnamese text emotion with PhoBERT and dictionary"""
    # Xử lý văn bản: chuẩn hóa, mở rộng viết tắt
    processed_text, features = text_processor.process(text)
    
    # Lấy điểm cảm xúc từ từ điển
    dict_score = features['sentiment_score']
    positive_count = features['positive_count']
    negative_count = features['negative_count']
    
    # Nếu từ điển có tín hiệu rất mạnh, ưu tiên từ điển
    if positive_count >= 2 and negative_count == 0:
        sentiment = "POSITIVE"
    elif negative_count >= 2 and positive_count == 0:
        sentiment = "NEGATIVE"
    elif abs(dict_score) >= 3:
        sentiment = "POSITIVE" if dict_score > 0 else "NEGATIVE"
    else:
        # Sử dụng PhoBERT model
        if sentiment_pipeline:
            try:
                # Tokenize with PhoBERT tokenizer (handles Vietnamese word segmentation)
                result = sentiment_pipeline(processed_text[:256])[0]
                label = result['label'].upper()
                score = result['score']
                
                # Map label to our format
                model_sentiment = LABEL_MAPPING.get(label, "NEUTRAL")
                
                # Combine model prediction with dictionary
                # If dictionary has signal and model agrees or is neutral, trust dictionary
                if dict_score > 0.5 and model_sentiment != "NEGATIVE":
                    sentiment = "POSITIVE"
                elif dict_score < -0.5 and model_sentiment != "POSITIVE":
                    sentiment = "NEGATIVE"
                elif abs(dict_score) < 0.3:
                    # Weak dictionary signal, trust model
                    sentiment = model_sentiment
                else:
                    # Medium dictionary signal, combine
                    if dict_score > 0 and model_sentiment == "POSITIVE":
                        sentiment = "POSITIVE"
                    elif dict_score < 0 and model_sentiment == "NEGATIVE":
                        sentiment = "NEGATIVE"
                    else:
                        sentiment = model_sentiment
                    
            except Exception as e:
                print(f"Model error: {e}")
                # Fallback to dictionary only
                if dict_score > 0.5:
                    sentiment = "POSITIVE"
                elif dict_score < -0.5:
                    sentiment = "NEGATIVE"
                else:
                    sentiment = "NEUTRAL"
        else:
            # No model available, use dictionary only
            if dict_score > 0.5:
                sentiment = "POSITIVE"
            elif dict_score < -0.5:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
    
    return {
        "input_text": text,
        "sentiment": sentiment
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    result = classify_emotion(text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
