# THIẾT KẾ HỆ THỐNG - APP PHÂN TÍCH CẢM XÚC TIẾNG VIỆT

## 1. TỔNG QUAN HỆ THỐNG

Ứng dụng web phân tích cảm xúc văn bản tiếng Việt sử dụng mô hình PhoBERT kết hợp với từ điển cảm xúc.

### Mục tiêu

- Phân loại văn bản tiếng Việt thành 3 loại: POSITIVE, NEUTRAL, NEGATIVE
- Hỗ trợ tiếng Việt không dấu và viết tắt
- Giao diện đơn giản, dễ sử dụng
- Lưu lịch sử phân loại

---

## 2. KIẾN TRÚC TỔNG QUAN

```
┌─────────────────────────────────────────────────────────────┐
│                        NGƯỜI DÙNG                            │
│                     (Trình duyệt Web)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Request/Response
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Nhập văn bản│  │  Hiển thị KQ │  │  Lịch sử     │      │
│  └──────────────┘  └──────────────┘  │  (localStorage)│     │
│                                       └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /classify
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   BACKEND (Flask Server)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              app.py (Main Application)               │   │
│  │  - Route handler: / và /classify                     │   │
│  │  - Điều phối xử lý văn bản và phân loại              │   │
│  └────────────┬─────────────────────────┬────────────────┘  │
│               │                         │                    │
│  ┌────────────▼──────────────┐  ┌──────▼─────────────────┐ │
│  │ VietnameseTextProcessor   │  │  PhoBERT Model        │ │
│  │ (vietnamese_processor.py) │  │  (Transformers)       │ │
│  │                           │  │                       │ │
│  │ - Chuẩn hóa văn bản       │  │ - Tokenizer           │ │
│  │ - Mở rộng viết tắt        │  │ - Model PhoBERT       │ │
│  │ - Từ điển cảm xúc         │  │ - Sentiment Pipeline  │ │
│  │ - Tính điểm cảm xúc       │  │                       │ │
│  └───────────────────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. LUỒNG XỬ LÝ CHÍNH (FLOWCHART)

```
                    ┌─────────────────┐
                    │   NGƯỜI DÙNG    │
                    │  Nhập văn bản   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Frontend (JS)  │
                    │  Gửi POST       │
                    │  /classify      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Flask Server  │
                    │   Nhận request  │
                    └────────┬────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │    VietnameseTextProcessor.process()   │
        │                                        │
        │  1. Chuẩn hóa văn bản                 │
        │     - Lowercase                        │
        │     - Loại bỏ ký tự đặc biệt          │
        │                                        │
        │  2. Mở rộng viết tắt                  │
        │     - k → không                        │
        │     - dc → được                        │
        │     - mk → mình                        │
        │                                        │
        │  3. Phân tích từ điển                 │
        │     - Đếm từ tích cực                 │
        │     - Đếm từ tiêu cực                 │
        │     - Phát hiện phủ định              │
        │     - Phát hiện cường độ              │
        │     - Tính điểm cảm xúc               │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │      Quyết định phương pháp phân loại  │
        └────────┬───────────────────────────────┘
                 │
                 ├─────────────────┬──────────────────┐
                 │                 │                  │
                 ▼                 ▼                  ▼
        ┌────────────────┐  ┌─────────────┐  ┌──────────────┐
        │ Tín hiệu mạnh  │  │ Tín hiệu TB │  │ Tín hiệu yếu │
        │ từ từ điển     │  │ từ từ điển  │  │ từ từ điển   │
        │                │  │             │  │              │
        │ (≥2 từ cùng   │  │ (điểm TB)   │  │ (điểm thấp)  │
        │  loại hoặc    │  │             │  │              │
        │  |điểm| ≥ 3)  │  │             │  │              │
        └────────┬───────┘  └──────┬──────┘  └──────┬───────┘
                 │                 │                 │
                 ▼                 ▼                 ▼
        ┌────────────────┐  ┌─────────────┐  ┌──────────────┐
        │ Dùng từ điển   │  │ Kết hợp cả  │  │ Dùng PhoBERT │
        │ trực tiếp      │  │ từ điển +   │  │ Model        │
        │                │  │ PhoBERT     │  │              │
        └────────┬───────┘  └──────┬──────┘  └──────┬───────┘
                 │                 │                 │
                 └─────────┬───────┴─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Kết quả cuối   │
                  │  POSITIVE       │
                  │  NEUTRAL        │
                  │  NEGATIVE       │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Trả về JSON    │
                  │  cho Frontend   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Hiển thị KQ    │
                  │  + Lưu vào      │
                  │  localStorage   │
                  └─────────────────┘
```

---

## 4. CHI TIẾT CÁC THÀNH PHẦN

### 4.1 Frontend (templates/index.html)

**Chức năng:**

- Giao diện người dùng
- Nhập văn bản tiếng Việt
- Gửi request đến backend
- Hiển thị kết quả phân loại
- Lưu và hiển thị lịch sử

**Công nghệ:**

- HTML5, CSS3, JavaScript (Vanilla)
- LocalStorage API
- Fetch API

**Các tính năng:**

```
┌─────────────────────────────────────┐
│  1. Nhập văn bản                    │
│     - Textarea để nhập              │
│     - Nút "Phân loại cảm xúc"       │
│                                     │
│  2. Kiểm tra mẫu                    │
│     - Nút "Kiểm tra 10 câu mẫu"     │
│     - Tự động phân loại 10 câu      │
│                                     │
│  3. Lịch sử                         │
│     - Nút "Xem lịch sử"             │
│     - Hiển thị 20 bản ghi gần nhất  │
│     - Lưu tối đa 50 bản ghi         │
│                                     │
│  4. Hiển thị kết quả                │
│     - Văn bản đầu vào               │
│     - Nhãn cảm xúc (màu sắc)        │
│     - Animation mượt mà             │
└─────────────────────────────────────┘
```

### 4.2 Backend - Flask Server (app.py)

**Chức năng:**

- Xử lý HTTP requests
- Điều phối logic phân loại
- Kết hợp kết quả từ processor và model

**Routes:**

```python
GET  /          → Render trang chủ (index.html)
POST /classify  → Phân loại văn bản
                  Input:  {"text": "..."}
                  Output: {"input_text": "...", "sentiment": "POSITIVE"}
```

**Thuật toán phân loại:**

```
if (positive_count ≥ 2 AND negative_count == 0):
    return "POSITIVE"

elif (negative_count ≥ 2 AND positive_count == 0):
    return "NEGATIVE"

elif (|dict_score| ≥ 3):
    return "POSITIVE" if dict_score > 0 else "NEGATIVE"

else:
    # Sử dụng PhoBERT Model
    model_result = sentiment_pipeline(text)

    # Kết hợp với từ điển
    if (dict_score > 0.5 AND model != "NEGATIVE"):
        return "POSITIVE"
    elif (dict_score < -0.5 AND model != "POSITIVE"):
        return "NEGATIVE"
    elif (|dict_score| < 0.3):
        return model_result
    else:
        return combined_result
```

### 4.3 Vietnamese Text Processor (vietnamese_processor.py)

**Chức năng:**

- Xử lý văn bản tiếng Việt
- Chuẩn hóa và làm sạch
- Phân tích cảm xúc từ từ điển

**Các bước xử lý:**

```
Input: "Hom nay mk rat vui dc gap ban"

Step 1: Chuẩn hóa
  - Lowercase: "hom nay mk rat vui dc gap ban"
  - Loại bỏ ký tự đặc biệt
  - Loại bỏ khoảng trắng thừa

Step 2: Mở rộng viết tắt
  - mk → mình
  - rat → rất
  - dc → được
  - ban → bạn
  Result: "hôm nay mình rất vui được gặp bạn"

Step 3: Phân tích từ điển
  - Từ tích cực: ["vui"] → count = 1
  - Từ tiêu cực: [] → count = 0
  - Cường độ: ["rất"] → có
  - Phủ định: [] → không

Step 4: Tính điểm
  - Base score = 1 - 0 = 1
  - Có cường độ → score = 1 × 1.5 = 1.5
  - Không phủ định → score = 1.5

Output:
  - processed_text: "hôm nay mình rất vui được gặp bạn"
  - features: {
      positive_count: 1,
      negative_count: 0,
      has_intensifier: true,
      has_negation: false,
      sentiment_score: 1.5
    }
```

**Từ điển:**

- 50+ từ tích cực: tốt, hay, đẹp, vui, thích, yêu, tuyệt...
- 50+ từ tiêu cực: tệ, xấu, dở, buồn, ghét, chán, kém...
- 80+ viết tắt: k→không, dc→được, mk→mình, bn→bạn...
- Từ phủ định: không, chẳng, chả, chưa...
- Từ cường độ: rất, cực, quá, lắm, siêu...

### 4.4 PhoBERT Model (Transformer Architecture)

**Mô hình:**

- Base: `vinai/phobert-base-v2`
- Fine-tuned: `wonrax/phobert-base-vietnamese-sentiment`
- Fallback: PhoBERT base + custom classification head

**Kiến trúc Transformer:**

PhoBERT là mô hình BERT được pre-train trên corpus tiếng Việt lớn. Nó sử dụng kiến trúc Transformer với cơ chế Self-Attention.

```
┌─────────────────────────────────────────────────────────────┐
│                    KIẾN TRÚC PHOBERT                         │
│                                                              │
│  Input: "hôm nay mình rất vui được gặp bạn"                 │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  1. TOKENIZATION (Tokenizer)                       │     │
│  │                                                     │     │
│  │  Word Segmentation (RDRSegmenter):                 │     │
│  │  "hôm_nay mình rất vui được gặp bạn"               │     │
│  │                                                     │     │
│  │  Subword Tokenization (BPE):                       │     │
│  │  ["[CLS]", "hôm_nay", "mình", "rất", "vui",        │     │
│  │   "được", "gặp", "bạn", "[SEP]"]                   │     │
│  │                                                     │     │
│  │  Token IDs:                                         │     │
│  │  [2, 1234, 567, 89, 345, 678, 901, 234, 3]         │     │
│  └─────────────────────┬───────────────────────────────┘    │
│                        ↓                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  2. EMBEDDING LAYER                                │     │
│  │                                                     │     │
│  │  Token Embeddings (768 dim):                       │     │
│  │  - Mỗi token → vector 768 chiều                    │     │
│  │                                                     │     │
│  │  Position Embeddings:                              │     │
│  │  - Vị trí của token trong câu                      │     │
│  │                                                     │     │
│  │  Segment Embeddings:                               │     │
│  │  - Phân biệt các câu (nếu có nhiều câu)           │     │
│  │                                                     │     │
│  │  Output: [9 tokens × 768 dimensions]               │     │
│  └─────────────────────┬───────────────────────────────┘    │
│                        ↓                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  3. TRANSFORMER ENCODER (12 layers)                │     │
│  │                                                     │     │
│  │  ┌──────────────────────────────────────────┐      │     │
│  │  │  Layer 1                                 │      │     │
│  │  │  ┌────────────────────────────────────┐  │      │     │
│  │  │  │  Multi-Head Self-Attention (12)    │  │      │     │
│  │  │  │                                     │  │      │     │
│  │  │  │  Q = Query  (từ input)             │  │      │     │
│  │  │  │  K = Key    (từ input)             │  │      │     │
│  │  │  │  V = Value  (từ input)             │  │      │     │
│  │  │  │                                     │  │      │     │
│  │  │  │  Attention(Q,K,V) =                │  │      │     │
│  │  │  │    softmax(QK^T/√d_k) × V          │  │      │     │
│  │  │  │                                     │  │      │     │
│  │  │  │  → Mỗi từ "nhìn" tất cả các từ    │  │      │     │
│  │  │  │  → Hiểu context và mối quan hệ     │  │      │     │
│  │  │  └────────────────────────────────────┘  │      │     │
│  │  │                ↓                          │      │     │
│  │  │  ┌────────────────────────────────────┐  │      │     │
│  │  │  │  Add & Normalize                   │  │      │     │
│  │  │  │  (Residual Connection + LayerNorm) │  │      │     │
│  │  │  └────────────────────────────────────┘  │      │     │
│  │  │                ↓                          │      │     │
│  │  │  ┌────────────────────────────────────┐  │      │     │
│  │  │  │  Feed Forward Network              │  │      │     │
│  │  │  │  - Linear(768 → 3072)              │  │      │     │
│  │  │  │  - GELU activation                 │  │      │     │
│  │  │  │  - Linear(3072 → 768)              │  │      │     │
│  │  │  └────────────────────────────────────┘  │      │     │
│  │  │                ↓                          │      │     │
│  │  │  ┌────────────────────────────────────┐  │      │     │
│  │  │  │  Add & Normalize                   │  │      │     │
│  │  │  └────────────────────────────────────┘  │      │     │
│  │  └──────────────────────────────────────────┘      │     │
│  │                                                     │     │
│  │  ... (Lặp lại 11 lần nữa cho Layer 2-12)          │     │
│  │                                                     │     │
│  │  Output: Contextual embeddings [9 × 768]           │     │
│  └─────────────────────┬───────────────────────────────┘    │
│                        ↓                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  4. POOLING                                        │     │
│  │                                                     │     │
│  │  Lấy embedding của token [CLS]:                    │     │
│  │  - Token đầu tiên đại diện cho toàn bộ câu        │     │
│  │  - Vector 768 chiều                                │     │
│  │                                                     │     │
│  │  [CLS] embedding: [768 dimensions]                 │     │
│  └─────────────────────┬───────────────────────────────┘    │
│                        ↓                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  5. CLASSIFICATION HEAD                            │     │
│  │                                                     │     │
│  │  Linear Layer:                                     │     │
│  │  768 → 3 (NEGATIVE, NEUTRAL, POSITIVE)             │     │
│  │                                                     │     │
│  │  Logits: [-1.2, 0.3, 2.5]                          │     │
│  │           ↓                                         │     │
│  │  Softmax:                                           │     │
│  │  [0.05, 0.06, 0.89]                                │     │
│  │                                                     │     │
│  │  Argmax → LABEL_2 (POSITIVE)                       │     │
│  │  Confidence: 0.89 (89%)                            │     │
│  └─────────────────────┬───────────────────────────────┘    │
│                        ↓                                     │
│  Output: {                                                   │
│    "label": "LABEL_2",    // POSITIVE                       │
│    "score": 0.89          // 89% confidence                 │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

**Chi tiết Self-Attention Mechanism:**

```
Ví dụ: Phân tích từ "vui" trong câu "hôm nay mình rất vui"

┌─────────────────────────────────────────────────────────────┐
│  SELF-ATTENTION: Từ "vui" nhìn các từ khác                  │
│                                                              │
│  Input embeddings:                                           │
│  hôm_nay: [0.2, 0.5, ..., 0.1]  (768 dim)                  │
│  mình:    [0.3, 0.1, ..., 0.4]                              │
│  rất:     [0.8, 0.2, ..., 0.3]  ← Cường độ                  │
│  vui:     [0.6, 0.9, ..., 0.7]  ← Từ đang xét              │
│                                                              │
│  Step 1: Tạo Q, K, V từ embeddings                          │
│  ────────────────────────────────────                       │
│  Q_vui = W_Q × embedding_vui    (Query: "vui" hỏi)         │
│  K_*   = W_K × embedding_*      (Key: các từ trả lời)      │
│  V_*   = W_V × embedding_*      (Value: giá trị thực)      │
│                                                              │
│  Step 2: Tính attention scores                              │
│  ────────────────────────────────────                       │
│  score(vui, hôm_nay) = Q_vui · K_hôm_nay / √64 = 0.3       │
│  score(vui, mình)    = Q_vui · K_mình / √64    = 0.2       │
│  score(vui, rất)     = Q_vui · K_rất / √64     = 0.9  ★    │
│  score(vui, vui)     = Q_vui · K_vui / √64     = 0.8       │
│                                                              │
│  Step 3: Softmax normalization                              │
│  ────────────────────────────────────                       │
│  attention_weights = softmax([0.3, 0.2, 0.9, 0.8])         │
│                    = [0.15, 0.10, 0.40, 0.35]              │
│                                                              │
│  → "vui" chú ý nhiều nhất đến "rất" (0.40)                 │
│  → Hiểu được "rất vui" là cụm từ có cường độ cao           │
│                                                              │
│  Step 4: Weighted sum                                       │
│  ────────────────────────────────────                       │
│  output_vui = 0.15×V_hôm_nay + 0.10×V_mình +               │
│               0.40×V_rất + 0.35×V_vui                       │
│                                                              │
│  → Embedding mới của "vui" đã chứa thông tin từ "rất"      │
│  → Context-aware representation                             │
└─────────────────────────────────────────────────────────────┘
```

**Multi-Head Attention (12 heads):**

```
┌─────────────────────────────────────────────────────────────┐
│  Thay vì 1 attention, PhoBERT dùng 12 attention heads       │
│                                                              │
│  Head 1: Học mối quan hệ ngữ pháp (chủ ngữ - động từ)      │
│  Head 2: Học mối quan hệ ngữ nghĩa (từ đồng nghĩa)         │
│  Head 3: Học cường độ (rất, cực, quá + tính từ)            │
│  Head 4: Học phủ định (không + động từ/tính từ)            │
│  ...                                                         │
│  Head 12: Học các pattern khác                              │
│                                                              │
│  Mỗi head học một khía cạnh khác nhau của ngôn ngữ         │
│  → Kết hợp lại → Hiểu sâu hơn về câu                        │
└─────────────────────────────────────────────────────────────┘
```

**Code Implementation trong app.py:**

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 1. Load tokenizer và model
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
model = AutoModelForSequenceClassification.from_pretrained(
    "wonrax/phobert-base-vietnamese-sentiment",
    num_labels=3  # NEGATIVE, NEUTRAL, POSITIVE
)

# 2. Tạo sentiment pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    device=-1  # CPU (-1), GPU (0)
)

# 3. Sử dụng
text = "hôm nay mình rất vui được gặp bạn"
result = sentiment_pipeline(text)

# Output:
# [{'label': 'LABEL_2', 'score': 0.8934567}]
#   LABEL_0 = NEGATIVE
#   LABEL_1 = NEUTRAL
#   LABEL_2 = POSITIVE
```

**Quá trình Training (đã được thực hiện trước):**

```
┌─────────────────────────────────────────────────────────────┐
│  PRE-TRAINING (PhoBERT Base)                                │
│                                                              │
│  Dataset: 20GB Vietnamese text (Wikipedia, News, etc.)      │
│  Tasks:                                                      │
│  1. Masked Language Modeling (MLM)                          │
│     Input:  "hôm nay tôi [MASK] vui"                        │
│     Target: "rất"                                            │
│     → Học hiểu ngữ cảnh tiếng Việt                          │
│                                                              │
│  2. Next Sentence Prediction (NSP)                          │
│     → Học mối quan hệ giữa các câu                          │
│                                                              │
│  Result: PhoBERT base model (vinai/phobert-base-v2)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  FINE-TUNING (Sentiment Analysis)                           │
│                                                              │
│  Dataset: Vietnamese sentiment dataset                       │
│  - Positive examples: "Sản phẩm tốt", "Rất hài lòng"       │
│  - Negative examples: "Dở quá", "Không thích"              │
│  - Neutral examples: "Bình thường", "Ổn"                    │
│                                                              │
│  Process:                                                    │
│  1. Freeze PhoBERT layers (hoặc fine-tune với lr thấp)     │
│  2. Train classification head (768 → 3)                     │
│  3. Optimize với labeled data                               │
│                                                              │
│  Result: wonrax/phobert-base-vietnamese-sentiment           │
└─────────────────────────────────────────────────────────────┘
```

**Ưu điểm của Transformer trong Sentiment Analysis:**

```
┌─────────────────────────────────────────────────────────────┐
│  1. Context-Aware (Hiểu ngữ cảnh)                           │
│     ────────────────────────────────                        │
│     "Không tốt"     → NEGATIVE (phủ định)                   │
│     "Không tệ"      → POSITIVE (phủ định của tiêu cực)      │
│     "Không tệ lắm"  → NEUTRAL (phủ định + cường độ)         │
│                                                              │
│     → Self-attention giúp model hiểu mối quan hệ            │
│                                                              │
│  2. Long-range Dependencies                                 │
│     ────────────────────────────────                        │
│     "Mặc dù giá hơi cao nhưng chất lượng rất tốt"          │
│     → Hiểu được "nhưng" đảo ngược sentiment                 │
│     → Kết luận: POSITIVE (chất lượng quan trọng hơn)        │
│                                                              │
│  3. Bidirectional (Hai chiều)                               │
│     ────────────────────────────────                        │
│     Đọc từ trái → phải VÀ phải → trái                       │
│     → Hiểu đầy đủ context xung quanh mỗi từ                │
│                                                              │
│  4. Transfer Learning                                        │
│     ────────────────────────────────                        │
│     Pre-train trên corpus lớn → Fine-tune cho task cụ thể   │
│     → Không cần nhiều labeled data                          │
│     → Độ chính xác cao hơn                                  │
└─────────────────────────────────────────────────────────────┘
```

**So sánh với phương pháp truyền thống:**

```
┌──────────────────────┬──────────────────┬──────────────────┐
│  Method              │  Dictionary      │  Transformer     │
├──────────────────────┼──────────────────┼──────────────────┤
│  "Không tốt"         │  POSITIVE ✗      │  NEGATIVE ✓      │
│  (phủ định)          │  (đếm "tốt")     │  (hiểu phủ định) │
├──────────────────────┼──────────────────┼──────────────────┤
│  "Giá cao nhưng OK"  │  NEGATIVE ✗      │  NEUTRAL ✓       │
│  (đảo ngược)         │  (đếm "cao")     │  (hiểu "nhưng")  │
├──────────────────────┼──────────────────┼──────────────────┤
│  "Tạm được"          │  POSITIVE ✗      │  NEUTRAL ✓       │
│  (ngữ cảnh)          │  (đếm "được")    │  (hiểu "tạm")    │
├──────────────────────┼──────────────────┼──────────────────┤
│  Speed               │  Fast (2ms)      │  Slow (100-300ms)│
├──────────────────────┼──────────────────┼──────────────────┤
│  Accuracy            │  ~70%            │  ~85-90%         │
└──────────────────────┴──────────────────┴──────────────────┘
```

**Tại sao dùng Hybrid Approach (Dictionary + Transformer):**

```
┌─────────────────────────────────────────────────────────────┐
│  Kết hợp ưu điểm của cả hai:                                │
│                                                              │
│  Dictionary:                                                 │
│  ✓ Nhanh (2ms)                                              │
│  ✓ Xử lý tốt các trường hợp đơn giản                        │
│  ✓ Không cần GPU                                            │
│  ✗ Không hiểu ngữ cảnh phức tạp                             │
│                                                              │
│  Transformer:                                                │
│  ✓ Độ chính xác cao (85-90%)                                │
│  ✓ Hiểu ngữ cảnh, phủ định, đảo ngược                       │
│  ✗ Chậm (100-300ms)                                         │
│  ✗ Cần nhiều tài nguyên                                     │
│                                                              │
│  Strategy:                                                   │
│  1. Dùng dictionary trước (fast check)                      │
│  2. Nếu tín hiệu mạnh → Trust dictionary                    │
│  3. Nếu tín hiệu yếu → Dùng Transformer                     │
│  4. Nếu tín hiệu trung bình → Kết hợp cả hai                │
│                                                              │
│  → Best of both worlds: Fast + Accurate                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. LUỒNG DỮ LIỆU (DATA FLOW)

```
┌──────────────┐
│  Người dùng  │
│  nhập text   │
└──────┬───────┘
       │
       │ "Hom nay mk rat vui"
       ▼
┌──────────────────────────────────────┐
│  Frontend JavaScript                 │
│  - Validate input                    │
│  - fetch('/classify', {text: ...})   │
└──────┬───────────────────────────────┘
       │
       │ HTTP POST
       │ {"text": "Hom nay mk rat vui"}
       ▼
┌──────────────────────────────────────┐
│  Flask Backend                       │
│  @app.route('/classify')             │
└──────┬───────────────────────────────┘
       │
       │ text = "Hom nay mk rat vui"
       ▼
┌──────────────────────────────────────┐
│  VietnameseTextProcessor             │
│  .process(text)                      │
│                                      │
│  Returns:                            │
│  - processed: "hôm nay mình rất vui" │
│  - features: {                       │
│      positive_count: 1,              │
│      negative_count: 0,              │
│      sentiment_score: 1.5            │
│    }                                 │
└──────┬───────────────────────────────┘
       │
       │ processed_text + features
       ▼
┌──────────────────────────────────────┐
│  classify_emotion()                  │
│  - Kiểm tra tín hiệu từ điển         │
│  - Quyết định dùng model hay không   │
└──────┬───────────────────────────────┘
       │
       │ (nếu cần)
       ▼
┌──────────────────────────────────────┐
│  PhoBERT Model                       │
│  sentiment_pipeline(processed_text)  │
│                                      │
│  Returns:                            │
│  - label: "LABEL_2"                  │
│  - score: 0.89                       │
└──────┬───────────────────────────────┘
       │
       │ model_result
       ▼
┌──────────────────────────────────────┐
│  Kết hợp kết quả                     │
│  - Từ điển + Model                   │
│  - Logic ưu tiên                     │
│                                      │
│  Final: "POSITIVE"                   │
└──────┬───────────────────────────────┘
       │
       │ JSON Response
       │ {
       │   "input_text": "Hom nay mk rat vui",
       │   "sentiment": "POSITIVE"
       │ }
       ▼
┌──────────────────────────────────────┐
│  Frontend                            │
│  - Hiển thị kết quả                  │
│  - Lưu vào localStorage              │
│  - Animation                         │
└──────────────────────────────────────┘
```

---

## 6. CƠ SỞ DỮ LIỆU (STORAGE)

### LocalStorage (Browser)

**Cấu trúc:**

```javascript
localStorage.sentimentHistory = [
  {
    text: "Hôm nay tôi rất vui",
    sentiment: "POSITIVE",
    timestamp: "2024-12-06T10:30:00.000Z",
  },
  {
    text: "Món ăn này dở quá",
    sentiment: "NEGATIVE",
    timestamp: "2024-12-06T10:25:00.000Z",
  },
  // ... tối đa 50 bản ghi
];
```

**Đặc điểm:**

- Lưu trữ phía client
- Không cần database server
- Dữ liệu tồn tại khi đóng/mở trình duyệt
- Bị xóa khi clear browser data
- Giới hạn: ~5-10MB

---

## 7. API SPECIFICATION

### POST /classify

**Request:**

```http
POST /classify HTTP/1.1
Content-Type: application/json

{
  "text": "Hôm nay tôi rất vui"
}
```

**Response (Success):**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "input_text": "Hôm nay tôi rất vui",
  "sentiment": "POSITIVE"
}
```

**Response (Error):**

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "No text provided"
}
```

---

## 8. DEPLOYMENT

### Yêu cầu hệ thống

```
┌─────────────────────────────────────┐
│  Server Requirements                │
│                                     │
│  - Python 3.8+                      │
│  - RAM: 2GB+ (4GB khuyến nghị)      │
│  - Disk: 2GB+ (cho models)          │
│  - CPU: 2 cores+                    │
│                                     │
│  Dependencies:                      │
│  - Flask 3.0.0                      │
│  - Transformers 4.36.0              │
│  - PyTorch 2.1.0                    │
│  - SentencePiece 0.1.99             │
└─────────────────────────────────────┘
```

### Cấu trúc thư mục

```
vietnamese-emotion-classifier/
│
├── app.py                      # Flask application chính
├── vietnamese_processor.py     # Xử lý văn bản tiếng Việt
├── requirements.txt            # Dependencies
├── README.md                   # Hướng dẫn sử dụng
├── ARCHITECTURE.md             # Tài liệu này
│
├── templates/
│   └── index.html             # Frontend UI
│
└── __pycache__/               # Python cache
```

---

## 9. PERFORMANCE & OPTIMIZATION

### Thời gian xử lý

```
┌─────────────────────────────────────────────┐
│  Component              │  Time (avg)       │
├─────────────────────────┼───────────────────┤
│  Text preprocessing     │  ~5ms             │
│  Dictionary analysis    │  ~2ms             │
│  PhoBERT inference      │  ~100-300ms (CPU) │
│  Total                  │  ~110-310ms       │
└─────────────────────────────────────────────┘
```

### Tối ưu hóa

1. **Model Loading:**

   - Load model 1 lần khi khởi động
   - Giữ model trong memory
   - Sử dụng model.eval() mode

2. **Text Processing:**

   - Cache từ điển trong memory
   - Giới hạn độ dài văn bản (256 tokens)
   - Xử lý batch nếu có nhiều requests

3. **Frontend:**
   - Debounce input nếu cần
   - Loading indicator
   - LocalStorage cho cache

---

## 10. SECURITY & ERROR HANDLING

### Bảo mật

```
┌─────────────────────────────────────┐
│  Security Measures                  │
│                                     │
│  1. Input Validation                │
│     - Kiểm tra text không rỗng      │
│     - Giới hạn độ dài input         │
│     - Sanitize special characters   │
│                                     │
│  2. CORS                            │
│     - Cấu hình CORS nếu cần         │
│                                     │
│  3. Rate Limiting                   │
│     - Giới hạn số request/phút      │
│                                     │
│  4. Error Handling                  │
│     - Try-catch cho model errors    │
│     - Fallback mechanisms           │
└─────────────────────────────────────┘
```

### Xử lý lỗi

```
Model Load Error
    ↓
Fallback to dictionary-only
    ↓
Continue operation

Model Inference Error
    ↓
Use dictionary score
    ↓
Return result

Empty Input
    ↓
Return 400 error
    ↓
Show error message
```

---

## 11. FUTURE IMPROVEMENTS

### Cải tiến có thể thực hiện

1. **Model:**

   - Fine-tune PhoBERT trên dataset riêng
   - Thêm nhiều nhãn cảm xúc (angry, sad, happy, etc.)
   - Hỗ trợ phân tích cảm xúc theo khía cạnh

2. **Features:**

   - Phân tích cảm xúc theo câu
   - Highlight từ khóa cảm xúc
   - Export lịch sử ra CSV/JSON
   - API key authentication

3. **Performance:**

   - Sử dụng GPU cho inference
   - Model quantization
   - Caching results

4. **Storage:**

   - Thêm database backend (PostgreSQL, MongoDB)
   - User accounts
   - Cloud storage

5. **UI/UX:**
   - Dark mode
   - Multi-language support
   - Real-time analysis
   - Visualization charts

---

## 12. TRIỂN KHAI VÀ KẾT QUẢ THỬ NGHIỆM

### 12.1 Quy trình triển khai

**Bước 1: Chuẩn bị môi trường**

```bash
# Clone repository
git clone <repository-url>
cd vietnamese-emotion-classifier

# Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

**Bước 2: Download models**

```
Khi chạy lần đầu, ứng dụng sẽ tự động download:
- PhoBERT base v2 (~500MB)
- Fine-tuned sentiment model (~500MB)
- Tokenizer files

Tổng dung lượng: ~1GB
Thời gian download: 5-10 phút (tùy tốc độ mạng)
```

**Bước 3: Khởi chạy ứng dụng**

```bash
# Chạy Flask server
python app.py

# Output:
# Loading vinai/phobert-base-v2...
# Using fine-tuned PhoBERT sentiment model
# * Running on http://0.0.0.0:5000
```

**Bước 4: Truy cập ứng dụng**

```
Mở trình duyệt và truy cập:
http://localhost:5000

Giao diện web sẽ hiển thị với 3 nút chính:
1. Phân loại cảm xúc (nhập text tùy ý)
2. Kiểm tra 10 câu mẫu (test tự động)
3. Xem lịch sử phân loại
```

### 12.2 Kết quả thử nghiệm với 10 câu mẫu

**Test Dataset:**

```
┌────┬─────────────────────────────────┬──────────────┬──────────────┬────────┐
│ #  │ Câu test                        │ Kỳ vọng      │ Kết quả      │ Đúng?  │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 1  │ Hôm nay tôi rất vui             │ POSITIVE     │ POSITIVE     │   ✓    │
│    │ (Tích cực rõ ràng)              │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 2  │ Món ăn này dở quá               │ NEGATIVE     │ NEGATIVE     │   ✓    │
│    │ (Tiêu cực rõ ràng)              │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 3  │ Thời tiết bình thường           │ NEUTRAL      │ NEUTRAL      │   ✓    │
│    │ (Trung tính)                    │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 4  │ Rat vui hom nay                 │ POSITIVE     │ POSITIVE     │   ✓    │
│    │ (Không dấu + viết tắt)          │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 5  │ Công việc ổn định               │ NEUTRAL      │ POSITIVE     │   ✗    │
│    │ (애매한 trường hợp)              │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 6  │ Phim này hay lắm                │ POSITIVE     │ POSITIVE     │   ✓    │
│    │ (Tích cực + cường độ)           │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 7  │ Tôi buồn vì thất bại            │ NEGATIVE     │ NEGATIVE     │   ✓    │
│    │ (Tiêu cực với lý do)            │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 8  │ Ngày mai đi học                 │ NEUTRAL      │ NEUTRAL      │   ✓    │
│    │ (Trung tính - sự kiện)          │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 9  │ Cảm ơn bạn rất nhiều            │ POSITIVE     │ POSITIVE     │   ✓    │
│    │ (Lời cảm ơn)                    │              │              │        │
├────┼─────────────────────────────────┼──────────────┼──────────────┼────────┤
│ 10 │ Mệt mỏi quá hôm nay             │ NEGATIVE     │ NEUTRAL      │   ✗    │
│    │ (Tiêu cực nhẹ)                  │              │              │        │
└────┴─────────────────────────────────┴──────────────┴──────────────┴────────┘

Kết quả: 8/10 đúng = 80% accuracy
```

### 12.3 Phân tích chi tiết kết quả

**Các trường hợp dự đoán đúng (8/10):**

```
✓ Câu 1: "Hôm nay tôi rất vui"
  ─────────────────────────────────────────────
  Dictionary: positive_count=1 ("vui"), intensifier=1 ("rất")
  → score = 1.5 (mạnh)
  PhoBERT: POSITIVE (0.92)
  Decision: POSITIVE ✓

✓ Câu 2: "Món ăn này dở quá"
  ─────────────────────────────────────────────
  Dictionary: negative_count=1 ("dở"), intensifier=1 ("quá")
  → score = -1.5 (mạnh)
  PhoBERT: NEGATIVE (0.88)
  Decision: NEGATIVE ✓

✓ Câu 3: "Thời tiết bình thường"
  ─────────────────────────────────────────────
  Dictionary: score = 0 (không có từ cảm xúc)
  PhoBERT: NEUTRAL (0.75)
  Decision: NEUTRAL ✓

✓ Câu 4: "Rat vui hom nay"
  ─────────────────────────────────────────────
  Preprocessing: "rat" → "rất", "hom nay" → "hôm nay"
  Dictionary: positive_count=1, intensifier=1
  → score = 1.5
  Decision: POSITIVE ✓
  (Xử lý tốt tiếng Việt không dấu)

✓ Câu 6: "Phim này hay lắm"
  ─────────────────────────────────────────────
  Dictionary: positive_count=1 ("hay"), intensifier=1 ("lắm")
  → score = 1.5
  PhoBERT: POSITIVE (0.89)
  Decision: POSITIVE ✓

✓ Câu 7: "Tôi buồn vì thất bại"
  ─────────────────────────────────────────────
  Dictionary: negative_count=1 ("buồn")
  PhoBERT: NEGATIVE (0.85)
  → Cả hai đều đồng ý
  Decision: NEGATIVE ✓

✓ Câu 8: "Ngày mai đi học"
  ─────────────────────────────────────────────
  Dictionary: score = 0 (không có từ cảm xúc)
  PhoBERT: NEUTRAL (0.82)
  Decision: NEUTRAL ✓

✓ Câu 9: "Cảm ơn bạn rất nhiều"
  ─────────────────────────────────────────────
  Dictionary: positive_count=1 ("cảm ơn"), intensifier=1 ("rất")
  → score = 1.5
  PhoBERT: POSITIVE (0.91)
  Decision: POSITIVE ✓
```

**Các trường hợp dự đoán sai (2/10):**

```
✗ Câu 5: "Công việc ổn định"
  ─────────────────────────────────────────────
  Kỳ vọng: NEUTRAL
  Kết quả: POSITIVE

  Phân tích:
  - Dictionary: "ổn" không có trong từ điển tích cực
  - PhoBERT: Hiểu "ổn định" là tích cực (0.68)
  - Trong tiếng Việt, "ổn định" thường mang nghĩa tích cực

  Nguyên nhân sai:
  - Label "NEUTRAL" có thể không chính xác
  - "Ổn định" trong context công việc thường là tốt
  - Model có thể đúng hơn label mong đợi

  Cải thiện:
  - Thêm "ổn", "ổn định" vào từ điển tích cực
  - Hoặc xem xét lại label mong đợi

✗ Câu 10: "Mệt mỏi quá hôm nay"
  ─────────────────────────────────────────────
  Kỳ vọng: NEGATIVE
  Kết quả: NEUTRAL

  Phân tích:
  - Dictionary: "mệt mỏi" không có trong từ điển tiêu cực
  - PhoBERT: NEUTRAL (0.55) - không chắc chắn
  - "Mệt mỏi" là cảm xúc tiêu cực nhẹ

  Nguyên nhân sai:
  - Từ điển thiếu "mệt", "mỏi", "mệt mỏi"
  - Model không đủ confident để phân loại NEGATIVE

  Cải thiện:
  - Thêm "mệt", "mỏi", "mệt mỏi" vào từ điển tiêu cực
  - Fine-tune model với nhiều ví dụ về cảm xúc nhẹ
```

### 12.4 Đánh giá hiệu suất

**Accuracy by Category:**

```
┌──────────────────┬───────────┬───────────┬──────────────┐
│ Category         │ Total     │ Correct   │ Accuracy     │
├──────────────────┼───────────┼───────────┼──────────────┤
│ POSITIVE         │ 4         │ 4         │ 100%         │
│ NEGATIVE         │ 3         │ 2         │ 67%          │
│ NEUTRAL          │ 3         │ 2         │ 67%          │
├──────────────────┼───────────┼───────────┼──────────────┤
│ OVERALL          │ 10        │ 8         │ 80%          │
└──────────────────┴───────────┴───────────┴──────────────┘
```

**Performance Metrics:**

```
┌─────────────────────────────────────────────────────────────┐
│  Metric                          │  Value                   │
├──────────────────────────────────┼──────────────────────────┤
│  Accuracy                        │  80%                     │
│  Precision (POSITIVE)            │  80% (4/5)               │
│  Recall (POSITIVE)               │  100% (4/4)              │
│  F1-Score (POSITIVE)             │  0.89                    │
│                                  │                          │
│  Precision (NEGATIVE)            │  100% (2/2)              │
│  Recall (NEGATIVE)               │  67% (2/3)               │
│  F1-Score (NEGATIVE)             │  0.80                    │
│                                  │                          │
│  Precision (NEUTRAL)             │  67% (2/3)               │
│  Recall (NEUTRAL)                │  67% (2/3)               │
│  F1-Score (NEUTRAL)              │  0.67                    │
└──────────────────────────────────┴──────────────────────────┘
```

**Response Time:**

```
┌─────────────────────────────────────────────────────────────┐
│  Component                       │  Time (ms)               │
├──────────────────────────────────┼──────────────────────────┤
│  Text preprocessing              │  3-5                     │
│  Dictionary analysis             │  1-2                     │
│  PhoBERT inference (CPU)         │  150-250                 │
│  Total (per request)             │  155-260                 │
│                                  │                          │
│  Average                         │  ~200ms                  │
│  Throughput                      │  ~5 requests/second      │
└──────────────────────────────────┴──────────────────────────┘
```

### 12.5 Điểm mạnh và điểm yếu

**Điểm mạnh:**

```
✓ Xử lý tốt cảm xúc POSITIVE (100% accuracy)
  - Nhận diện chính xác từ tích cực
  - Hiểu cường độ (rất, lắm, quá)
  - Xử lý lời cảm ơn

✓ Xử lý tốt tiếng Việt không dấu
  - "Rat vui hom nay" → POSITIVE ✓
  - Mở rộng viết tắt tự động

✓ Hybrid approach hiệu quả
  - Dictionary cho trường hợp đơn giản (nhanh)
  - PhoBERT cho trường hợp phức tạp (chính xác)

✓ Fallback mechanism
  - Nếu model lỗi, vẫn có dictionary
  - Hệ thống luôn trả về kết quả
```

**Điểm yếu:**

```
✗ Từ điển chưa đầy đủ
  - Thiếu "mệt mỏi", "ổn định"
  - Cần bổ sung thêm từ tiếng Việt thông dụng

✗ Khó phân biệt NEUTRAL vs POSITIVE/NEGATIVE nhẹ
  - "Công việc ổn định" → Nên là NEUTRAL hay POSITIVE?
  - "Mệt mỏi" → NEGATIVE nhẹ bị nhận là NEUTRAL

✗ Chạy trên CPU chậm
  - 200ms/request
  - Nếu có GPU: ~20-30ms/request (nhanh hơn 10x)

✗ Chưa xử lý tốt phủ định phức tạp
  - "Không tệ lắm" → Cần test thêm
  - "Chẳng hay ho gì" → Cần test thêm
```

### 12.6 Khuyến nghị cải thiện

**Ngắn hạn (1-2 tuần):**

```
1. Bổ sung từ điển
   ─────────────────────────────────────────────
   Thêm vào negative_words:
   - "mệt", "mỏi", "mệt mỏi", "kiệt sức"
   - "chán nản", "thất vọng", "buồn tẻ"

   Thêm vào positive_words:
   - "ổn", "ổn định", "tốt đẹp", "thuận lợi"

   Expected improvement: 80% → 85%

2. Tối ưu logic kết hợp
   ─────────────────────────────────────────────
   - Điều chỉnh threshold cho dictionary score
   - Cải thiện logic kết hợp dictionary + model

   Expected improvement: 80% → 85%

3. Thêm test cases
   ─────────────────────────────────────────────
   - Tăng từ 10 → 50 câu test
   - Bao gồm nhiều trường hợp edge cases
   - Phủ định, đảo ngược, ngữ cảnh phức tạp
```

**Trung hạn (1-2 tháng):**

```
4. Fine-tune PhoBERT
   ─────────────────────────────────────────────
   - Thu thập dataset tiếng Việt lớn hơn
   - Fine-tune trên domain cụ thể (review, comment, etc.)

   Expected improvement: 85% → 90%

5. Thêm GPU support
   ─────────────────────────────────────────────
   - Giảm response time: 200ms → 20-30ms
   - Tăng throughput: 5 req/s → 30-50 req/s

6. Thêm confidence score
   ─────────────────────────────────────────────
   - Hiển thị độ tin cậy của dự đoán
   - Cảnh báo khi confidence thấp
```

**Dài hạn (3-6 tháng):**

```
7. Multi-label classification
   ─────────────────────────────────────────────
   - Thêm nhãn: ANGRY, SAD, HAPPY, FEAR, SURPRISE
   - Aspect-based sentiment analysis

8. Real-time analysis
   ─────────────────────────────────────────────
   - WebSocket cho phân tích real-time
   - Streaming analysis cho văn bản dài

9. API và SDK
   ─────────────────────────────────────────────
   - RESTful API với authentication
   - Python SDK, JavaScript SDK
   - Rate limiting và caching
```

### 12.7 Kết luận triển khai

**Tổng kết:**

```
┌─────────────────────────────────────────────────────────────┐
│  Dự án: Vietnamese Emotion Classifier                       │
│  Công nghệ: Flask + PhoBERT + Dictionary                    │
│  Kết quả: 80% accuracy trên 10 câu test                     │
│                                                              │
│  Thành công:                                                 │
│  ✓ Triển khai thành công hybrid approach                    │
│  ✓ Xử lý tốt tiếng Việt không dấu và viết tắt              │
│  ✓ Giao diện đơn giản, dễ sử dụng                           │
│  ✓ Response time chấp nhận được (~200ms)                    │
│                                                              │
│  Cần cải thiện:                                              │
│  ⚠ Bổ sung từ điển đầy đủ hơn                               │
│  ⚠ Fine-tune model cho domain cụ thể                        │
│  ⚠ Thêm GPU support để tăng tốc độ                          │
│                                                              │
│  Đánh giá chung: ⭐⭐⭐⭐☆ (4/5)                              │
│  - Phù hợp cho demo, prototype, học tập                     │
│  - Cần cải thiện trước khi production                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 13. TÓM TẮT

Hệ thống phân tích cảm xúc tiếng Việt sử dụng kiến trúc hybrid:

**Ưu điểm:**

- ✅ Độ chính xác 80% trên test set
- ✅ Xử lý tốt tiếng Việt không dấu
- ✅ Hỗ trợ viết tắt và slang
- ✅ Fallback mechanism an toàn
- ✅ Giao diện đơn giản, dễ dùng
- ✅ Không cần database phức tạp

**Hạn chế:**

- ⚠️ Chạy trên CPU (chậm hơn GPU)
- ⚠️ Chỉ 3 nhãn cảm xúc cơ bản
- ⚠️ LocalStorage có giới hạn
- ⚠️ Không có user authentication
- ⚠️ Từ điển chưa đầy đủ

**Use Cases:**

- Phân tích feedback khách hàng
- Phân tích bình luận mạng xã hội
- Phân tích review sản phẩm
- Nghiên cứu sentiment analysis
- Demo và học tập

---

**Phiên bản:** 1.0  
**Ngày cập nhật:** 06/12/2024  
**Tác giả:** Vietnamese Emotion Classifier Team
