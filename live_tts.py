import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import os

def setup_model(config_path, model_path, tokenizer_path):
    """
    Load the model configuration and weights.
    """
    config = XttsConfig()
    config.load_json(config_path)
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_path=model_path, vocab_path=tokenizer_path, use_deepspeed=False)
    model.cuda()
    return model

def synthesize_speech(model, text, reference_audio, output_dir, temperature=0.2):
    """
    Generate speech from text using the model.

    Args:
        model: The loaded TTS model.
        text: The text to synthesize.
        reference_audio: Path to the reference audio file for conditioning.
        output_dir: Directory to save the generated audio.
        temperature: Sampling temperature for synthesis.

    Returns:
        Path to the saved audio file.
    """
    try:
        # Extract conditioning latents and speaker embedding
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=[reference_audio])

        # Generate speech
        out = model.inference(text, 'ko', gpt_cond_latent, speaker_embedding, temperature=temperature)

        # Save audio file
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"output_{len(os.listdir(output_dir)) + 1}.wav")
        torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)

        return output_path
    except Exception as e:
        print(f"Error during synthesis: {e}")
        return None

def main():
    tokenizer_path = '/home/metaai2/byeonguk_work/I-live-A-commerce/XTTS/XTTS_v2.0_original_model_files/vocab.json'
    model_path = '/home/metaai2/byeonguk_work/I-live-A-commerce/XTTS/GPT_XTTS_Multi_Speaker_FT-December-24-2024_03+00AM-0000000/best_model_2244.pth'
    config_path = '/home/metaai2/byeonguk_work/I-live-A-commerce/XTTS/GPT_XTTS_Multi_Speaker_FT-December-24-2024_03+00AM-0000000/config.json'

    output_dir = "/home/metaai2/byeonguk_work/I-live-A-commerce/XTTS/fix_audio_file"

    model = setup_model(config_path, model_path, tokenizer_path)

    # Gender selection
    
    gender = input()
    if gender == '남자':
        reference_audio = '/home/metaai2/byeonguk_work/I-live-A-commerce/XTTS/itsub/content/wavs/audio1.wav'
    elif gender == '여자':
        reference_audio =  '/home/metaai2/byeonguk_work/I-live-A-commerce/XTTS/iu/content/wavs/audio1.wav'
    

    text = "동해물과 백두산이 마르고 닳도록. 하느님이 보우하사 우리나라 만세. 무궁화 삼천리 화려강산산"

    output_path = synthesize_speech(model, text, reference_audio, output_dir)
    if output_path:
        print(f"Generated audio saved at: {output_path}")

if __name__ == "__main__":
    main()
