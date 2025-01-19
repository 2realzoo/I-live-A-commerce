import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import os

tokenizer_path = './XTTS/XTTS_v2.0_original_model_files/vocab.json'
model_path = './XTTS/GPT_XTTS_Multi_Speaker_FT-December-26-2024_03+59AM-0000000/best_model_2244.pth'
config_path = './XTTS/GPT_XTTS_Multi_Speaker_FT-December-26-2024_03+59AM-0000000/config.json'

config = XttsConfig()
config.load_json(config_path)
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_path=model_path, vocab_path=tokenizer_path, use_deepspeed=False)
model.cuda()

def make_tts(category, channel, text, gender):
    output_dir = f"./{category}_{channel_num}/tts"
    os.makedirs(output_dir, exist_ok=True)
    
    if gender == '남자':
        reference_audio = ['./XTTS/itsub/content/wavs/audio1.wav']
        break
    elif gender == '여자':
        reference_audio = ['./XTTS/iu/content/wavs/audio1.wav']
        break

    try:
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=reference_audio)
        
        out = model.inference(text, 'ko', gpt_cond_latent, speaker_embedding, temperature=0.2)

        output_path = os.path.join(output_dir, f"{category}_{channel_num}.wav")
        torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
        output_wavs.append(output_path)

    except Exception as e:
        print(f"오류 발생: {e}")