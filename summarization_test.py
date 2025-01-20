from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

def clean_summary(summary):
    """
    요약 결과를 깔끔하게 정리
    """
    summary = summary.strip()
    if not summary.endswith(('.', '!', '?')):
        summary += '.'
    return summary

tokenizer = PreTrainedTokenizerFast.from_pretrained("EbanLee/kobart-summary-v3")
model = BartForConditionalGeneration.from_pretrained("EbanLee/kobart-summary-v3")

# 입력 파일 읽기
input_file = "/home/metaai2/byeonguk_work/I-live-A-commerce/test/stt_file_test.txt"
with open(input_file, "r", encoding="utf-8") as f:
    input_text = f.read().strip()

inputs = tokenizer(input_text, return_tensors="pt", padding="max_length", truncation=True, max_length=1026)

summary_text_ids = model.generate(
    input_ids=inputs['input_ids'],
    attention_mask=inputs['attention_mask'],
    bos_token_id=model.config.bos_token_id,
    eos_token_id=model.config.eos_token_id,
    max_length=80,  
    min_length=20,  
    length_penalty=1.5,
    num_beams=4,
    repetition_penalty=1.3,
    no_repeat_ngram_size=3,
    early_stopping=True,
)

summary = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
cleaned_summary = clean_summary(summary)

print("Summary:", cleaned_summary)
