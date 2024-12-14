import re
from collections import Counter, defaultdict
from nlp.utils import remove_stopwords, tokenize_text
from nlp.llm_model import LLMModel, sentiment_prompt, sentiment_user_prompt_template
from langchain.chat_models import ChatOllama, ChatOpenAI
from transformers import AutoModelForSequenceClassification

class SentimentAnalyzer:
    def __init__(self, sentence_model, token_model):
        # 모델 초기화
        self.sentence_model = sentence_model
        self.token_model = token_model

    def analyze_sentence_sentiment(self, comments, most_k=5):
        result = defaultdict(dict)
        all_tokens = []
        for comment in comments:
            score = self.extract_float(self.sentence_model.invoke(comment)) 
            result[comment]['sentiment_score'] = score
            if 'tokens' not in result[comment]:
                result[comment]['tokens'] = []
            tokens = remove_stopwords(tokenize_text(comment))
            result[comment]['tokens'].extend(tokens)
            all_tokens.extend(tokens)
        
        token_counter = Counter(all_tokens)
        most_common_token = token_counter.most_common(most_k)
        return result, token_counter, most_common_token

    def extract_float(self, data):
        # 정규식을 이용해 숫자 (소수점 포함) 추출
        match = re.search(r'\d+\.\d+', data)
        if match:
            return float(match.group())  # 매칭된 숫자를 float으로 변환
        else:
            raise ValueError("숫자를 찾을 수 없습니다.")  # 숫자가 없을 경우 에러 처리

if __name__ == "__main__":
    sentence_model = LLMModel(ChatOpenAI(model='gpt-4o-mini'), sentiment_prompt, sentiment_user_prompt_template)
    token_model = AutoModelForSequenceClassification.from_pretrained("jaehyeong/koelectra-base-v3-generalized-sentiment-analysis")
    sentiment_model = SentimentAnalyzer(sentence_model, token_model)
    
    import pandas as pd
    
    data = pd.read_csv('2_1495243_comment_log.csv')
    print(sentiment_model.analyze_sentence_sentiment(data['댓글']))