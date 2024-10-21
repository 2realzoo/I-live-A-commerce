import os
import torch
from moviepy.editor import VideoFileClip
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

class BeforeSum:
    def __init__(self, num):
        load_dotenv()
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.llm_model = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.5)
        self.num = num
    
    #영상 -> 오디오 추출
    def video2voice(self):
        video = VideoFileClip(f'streaming_{self.num}.mp4')
        video.audio.write_audiofile(f'streaming_{self.num}.mp3')
        
    #오디오 -> 텍스트 추출
    def voice2text(self):
        self.video2voice()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model_id = "openai/whisper-large-v3"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )

        model.to(device)
        processor = AutoProcessor.from_pretrained(model_id)
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens = 128,
            chunk_length_s = 30,
            batch_size = 16,
            return_timestamps = True,
            torch_dtype=torch_dtype,
            device=device
        )
    
        result_openai = pipe(f'streaming_{self.num}.mp3')
    
        with open(f'streaming_{self.num}.txt', 'w', encoding='utf-8') as stt_file:
            stt_file.write(result_openai["text"])
     
    #텍스트 => 이전 방송 내용을 요약해서 제공
    def before_streaming_summarize(self):
        self.voice2text()
        
        text_loader = TextLoader(f'streaming_{self.num}.txt', encoding='utf-8')
        document = text_loader.load()
        document_splitter = RecursiveCharacterTextSplitter(chunk_size = 40, chunk_overlap=0)
        docs = document_splitter.create_documents([document[0].page_content])
        
        embeddings = OpenAIEmbeddings()
        embeddings.embed_documents(document[0].page_content)

        persist_directory = f'{self.num}DB'
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        vectordb.persist()
        retriver = vectordb.as_retriever().get_relevant_documents('진행상황 요약')
        
        sum_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template('''{retriver}에 있는 내용을 말해.
                                                당신은 라이브 커머스 방송 매니저야.
                                                지금 들어온 시청자를 위해 앞에 내용을 이야기해주는 상황이야. 
                                                시청자와 소통했던 내용 및 이벤트 진행상황에 대해서 말하거나 시청자가 묻는 내용에 대해서 이야기해.
                                                만약 묻지 않은 내용이 있으면 답하지 마.
                                                말투는 {retriver}에 있는 말투를 따라해.
                                                전체적으로 말을 자연스럽게 만들어.
                                                '''),
                HumanMessagePromptTemplate.from_template('{input}')
            ]
        )
        
        sum_chain = LLMChain(
            llm = self.llm_model,
            prompt = sum_prompt
        )
        
        return sum_chain.predict(input='', retriver=retriver) 