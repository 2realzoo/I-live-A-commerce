import torch
from moviepy.editor import VideoFileClip
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os
from mutagen.mp3 import MP3

#영상 -> 오디오 추출
def video2voice(category, channel_num):
    """영상에서 오디오 추출 후 MP3 파일 경로 반환."""
    mp3_path = f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.mp3'
    video_path = f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.mp4'

    # MP4 파일 존재 여부 확인
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"[ERROR] 비디오 파일이 없습니다: {video_path}")

    # 오디오 추출
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(mp3_path)
    return mp3_path

# MP3 파일 길이 확인
def get_audio_duration(mp3_path):
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"[ERROR] 파일을 찾을 수 없습니다: {mp3_path}")
    audio = MP3(mp3_path)
    return int(audio.info.length)  # 초 단위로 반환

# 오디오 -> 텍스트 추출
def voice2text(category, channel_num):
    mp3_path = video2voice(category, channel_num)
    txt_path = f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.txt'
    processed_duration_path = f'DB/{category}_{channel_num}/processed_duration.txt'

    # 이전 처리된 길이 확인
    processed_duration = 0
    if os.path.exists(processed_duration_path):
        with open(processed_duration_path, 'r') as f:
            processed_duration = int(f.read().strip())

    # 현재 MP3의 전체 길이
    total_duration = get_audio_duration(mp3_path)

    # 새로 처리할 범위 계산
    if processed_duration >= total_duration:
        print("[INFO] 새로 처리할 오디오가 없습니다.")
        return txt_path

    print(f"[INFO] 새로운 처리 범위: {processed_duration}s ~ {total_duration}s")

    # Whisper 모델 설정
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = 'openai/whisper-large-v3'

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        'automatic-speech-recognition',
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=256,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device
    )

    # 새로 처리할 부분을 임시 MP3로 분리
    temp_mp3_path = f'DB/{category}_{channel_num}/temp_{category}_{channel_num}.mp3'
    start_time = processed_duration
    end_time = total_duration
    os.system(f"ffmpeg -y -i {mp3_path} -ss {start_time} -to {end_time} -c copy {temp_mp3_path}")

    # Whisper 실행
    print(f"[INFO] Whisper 모델 실행 중: {temp_mp3_path}")
    result = pipe(temp_mp3_path)

    # 결과 텍스트 추가 저장
    with open(txt_path, 'a', encoding='utf-8') as f:
        f.write(result['text'])
    print(f"[INFO] 텍스트 파일 갱신 완료: {txt_path}")

    # 처리된 길이 업데이트
    with open(processed_duration_path, 'w') as f:
        f.write(str(total_duration))
    print(f"[INFO] 처리된 오디오 길이 업데이트 완료: {total_duration}s")

    # 임시 파일 삭제
    if os.path.exists(temp_mp3_path):
        os.remove(temp_mp3_path)

    return txt_path