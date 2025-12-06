import re
from typing import Dict, List

class VietnameseTextProcessor:
    """Xử lý văn bản tiếng Việt: chuẩn hóa, thêm dấu, mở rộng viết tắt"""
    
    def __init__(self):
        # Từ điển viết tắt phổ biến
        self.abbreviations = {
            'k': 'không',
            'ko': 'không',
            'kg': 'không',
            'kh': 'không',
            'khong': 'không',
            'dc': 'được',
            'đc': 'được',
            'duoc': 'được',
            'vs': 'với',
            'v': 'với',
            'j': 'gì',
            'gi': 'gì',
            'r': 'rồi',
            'roi': 'rồi',
            'ntn': 'như thế nào',
            'sao': 'sao',
            'tks': 'cảm ơn',
            'thanks': 'cảm ơn',
            'thnks': 'cảm ơn',
            'cx': 'cũng',
            'cug': 'cũng',
            'cung': 'cũng',
            'mk': 'mình',
            'mik': 'mình',
            'minh': 'mình',
            'bn': 'bạn',
            'b': 'bạn',
            'ban': 'bạn',
            'nv': 'như vậy',
            'nva': 'như vậy',
            'ok': 'được',
            'oke': 'được',
            'okela': 'được',
            'oki': 'được',
            'nc': 'nói chuyện',
            'ms': 'mới',
            'moi': 'mới',
            'wa': 'quá',
            'qua': 'quá',
            'z': 'vậy',
            'v': 'vậy',
            'vay': 'vậy',
            'ny': 'này',
            'nay': 'này',
            'kia': 'kia',
            'do': 'đó',
            'day': 'đây',
            'đay': 'đây',
            'lm': 'làm',
            'lam': 'làm',
            'bik': 'biết',
            'bit': 'biết',
            'biet': 'biết',
            'hok': 'học',
            'hoc': 'học',
            'hix': 'buồn',
            'hiz': 'buồn',
            'hjz': 'buồn',
            'uk': 'ừ',
            'uh': 'ừ',
            'u': 'ừ',
            'oke': 'được',
            'tl': 'trả lời',
            'rep': 'trả lời',
            'reply': 'trả lời',
            'sr': 'xin lỗi',
            'sry': 'xin lỗi',
            'sorry': 'xin lỗi',
            'xl': 'xin lỗi',
            'xin loi': 'xin lỗi',
            'cam on': 'cảm ơn',
            'thank': 'cảm ơn',
            'ty': 'cảm ơn',
            'tui': 'tôi',
            'toy': 'tôi',
            'toi': 'tôi',
            'mjk': 'mình',
            'mjnh': 'mình',
            'nha': 'nhé',
            'nhe': 'nhé',
            'di': 'đi',
            'den': 'đến',
            'đen': 'đến',
            'trc': 'trước',
            'truoc': 'trước',
            'sau': 'sau',
            'nhiu': 'nhiều',
            'nhieu': 'nhiều',
            'rat': 'rất',
            'qk': 'quá',
            'vcl': 'vãi',
            'vl': 'vãi',
            'dm': 'đáng ghét',
            'cc': 'tệ',
            'nch': 'nói chuyện',
            'ib': 'nhắn tin',
            'inbox': 'nhắn tin',
            'sdt': 'số điện thoại',
            'dt': 'điện thoại',
            'dien thoai': 'điện thoại',
            'nt': 'nhắn tin',
            'zl': 'zalo',
            'fb': 'facebook',
            'face': 'facebook',
            'fbook': 'facebook',
        }
        
        # Từ điển cảm xúc tích cực
        self.positive_words = {
            'tốt', 'hay', 'đẹp', 'tuyệt', 'vời', 'tuyệt vời', 'xuất sắc', 'tốt',
            'yêu', 'thích', 'vui', 'hạnh phúc', 'vui vẻ', 'tuyệt', 'tốt lắm',
            'ok', 'oke', 'được', 'ngon', 'chất', 'đỉnh', 'pro', 'giỏi',
            'cảm ơn', 'thanks', 'thank', 'tks', 'cám ơn', 'camon',
            'hài lòng', 'ưng ý', 'hoàn hảo', 'tốt nhất', 'tuyệt nhất',
            'thành công', 'hiệu quả', 'nhanh', 'tiện', 'dễ', 'đơn giản',
            'chuyên nghiệp', 'nhiệt tình', 'tận tâm', 'chu đáo', 'ân cần',
        }
        
        # Từ điển cảm xúc tiêu cực
        self.negative_words = {
            'tệ', 'xấu', 'dở', 'kém', 'tồi', 'không tốt', 'không hay',
            'ghét', 'chán', 'buồn', 'tức', 'giận', 'thất vọng', 'tệ hại',
            'không thích', 'ko thích', 'k thích', 'không ưng', 'không được',
            'lỗi', 'hỏng', 'hư', 'chậm', 'lâu', 'khó', 'phức tạp',
            'tệ quá', 'dở quá', 'kém quá', 'tồi tệ', 'thảm họa',
            'không chuyên nghiệp', 'thái độ tệ', 'phục vụ kém', 'lừa đảo',
            'scam', 'lừa', 'gian lận', 'không uy tín', 'mất tiền',
            'vcl', 'vl', 'dm', 'cc', 'shit', 'fuck', 'đéo', 'đm',
        }
        
        # Từ điển phủ định
        self.negation_words = {
            'không', 'chẳng', 'chả', 'chưa', 'đừng', 'đừng có',
            'không có', 'ko', 'k', 'kg', 'kh', 'khong',
        }
        
        # Từ điển cường độ
        self.intensifiers = {
            'rất', 'cực', 'cực kỳ', 'vô cùng', 'hết sức', 'quá', 'lắm',
            'nhiều', 'mạnh', 'siêu', 'cực kì', 'rat', 'qua', 'wa',
        }
    
    def normalize_text(self, text: str) -> str:
        """Chuẩn hóa văn bản: lowercase, loại bỏ ký tự đặc biệt"""
        # Lowercase
        text = text.lower()
        
        # Loại bỏ emoji và ký tự đặc biệt (giữ lại dấu câu cơ bản)
        text = re.sub(r'[^\w\s\.,!?àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def expand_abbreviations(self, text: str) -> str:
        """Mở rộng các từ viết tắt"""
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Loại bỏ dấu câu để kiểm tra
            clean_word = re.sub(r'[.,!?]', '', word)
            
            if clean_word in self.abbreviations:
                expanded_words.append(self.abbreviations[clean_word])
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def add_sentiment_features(self, text: str) -> Dict:
        """Phân tích đặc trưng cảm xúc từ văn bản"""
        words = set(text.split())
        
        # Đếm từ tích cực và tiêu cực
        positive_count = len(words.intersection(self.positive_words))
        negative_count = len(words.intersection(self.negative_words))
        
        # Kiểm tra phủ định
        has_negation = len(words.intersection(self.negation_words)) > 0
        
        # Kiểm tra cường độ
        has_intensifier = len(words.intersection(self.intensifiers)) > 0
        
        # Tính điểm cảm xúc
        sentiment_score = positive_count - negative_count
        
        # Điều chỉnh nếu có phủ định
        if has_negation:
            sentiment_score = -sentiment_score
        
        # Tăng cường độ
        if has_intensifier:
            sentiment_score *= 1.5
        
        return {
            'positive_count': positive_count,
            'negative_count': negative_count,
            'has_negation': has_negation,
            'has_intensifier': has_intensifier,
            'sentiment_score': sentiment_score
        }
    
    def process(self, text: str) -> tuple:
        """Xử lý toàn bộ: chuẩn hóa, mở rộng viết tắt, phân tích cảm xúc"""
        # Chuẩn hóa
        normalized = self.normalize_text(text)
        
        # Mở rộng viết tắt
        expanded = self.expand_abbreviations(normalized)
        
        # Phân tích cảm xúc
        features = self.add_sentiment_features(expanded)
        
        return expanded, features
