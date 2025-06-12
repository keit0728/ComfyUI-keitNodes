from typing import Any
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import langid
import os
import folder_paths
from huggingface_hub import snapshot_download

MODEL_CONFIGS = {
    "418M": {
        "model_name": "facebook/m2m100_418M",
        "cache_dir": "m2m100_418M",
    },
    "1.2B": {
        "model_name": "facebook/m2m100_1.2B",
        "cache_dir": "m2m100_1.2B",
    },
}


class M2MTranslator:
    """
    M2M-100 multilingual translation
    """

    # Class variables to hold models (shared across multiple nodes)
    _model: M2M100ForConditionalGeneration | None = None
    _tokenizer: Any | None = None
    _current_model_name: str | None = None

    def __init__(self):
        self.base_cache_dir = os.path.join(folder_paths.models_dir, "keit-nodes")

    @classmethod
    def INPUT_TYPES(cls):
        # List of languages supported by M2M-100 (selected major ones)
        languages = [
            "auto_detect",
            "ja",  # Japanese
            "en",  # English
            "zh",  # Chinese
            "ko",  # Korean
            "fr",  # French
            "de",  # German
            "es",  # Spanish
            "ru",  # Russian
            "ar",  # Arabic
            "hi",  # Hindi
            "pt",  # Portuguese
            "it",  # Italian
            "tr",  # Turkish
            "th",  # Thai
            "vi",  # Vietnamese
            "pl",  # Polish
            "nl",  # Dutch
            "sv",  # Swedish
            "da",  # Danish
            "no",  # Norwegian
            "fi",  # Finnish
            "cs",  # Czech
            "hu",  # Hungarian
            "ro",  # Romanian
            "bg",  # Bulgarian
            "hr",  # Croatian
            "sk",  # Slovak
            "sl",  # Slovenian
            "et",  # Estonian
            "lv",  # Latvian
            "lt",  # Lithuanian
            "uk",  # Ukrainian
            "be",  # Belarusian
            "mk",  # Macedonian
            "sq",  # Albanian
            "sr",  # Serbian
            "bs",  # Bosnian
            "is",  # Icelandic
            "ga",  # Irish
            "cy",  # Welsh
            "ca",  # Catalan
            "fa",  # Persian
            "ur",  # Urdu
            "bn",  # Bengali
            "ta",  # Tamil
            "te",  # Telugu
            "kn",  # Kannada
            "ml",  # Malayalam
            "gu",  # Gujarati
            "pa",  # Punjabi
            "mr",  # Marathi
            "ne",  # Nepali
            "si",  # Sinhala
            "my",  # Burmese
            "km",  # Khmer
            "lo",  # Lao
            "ka",  # Georgian
            "hy",  # Armenian
            "az",  # Azerbaijani
            "kk",  # Kazakh
            "uz",  # Uzbek
            "mn",  # Mongolian
            "he",  # Hebrew
            "yi",  # Yiddish
            "sw",  # Swahili
            "zu",  # Zulu
            "xh",  # Xhosa
            "af",  # Afrikaans
            "am",  # Amharic
            "ha",  # Hausa
            "ig",  # Igbo
            "yo",  # Yoruba
            "so",  # Somali
            "mg",  # Malagasy
            "id",  # Indonesian
            "ms",  # Malay
            "tl",  # Tagalog
            "jv",  # Javanese
            "su",  # Sundanese
            "ceb",  # Cebuano
        ]

        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "こんにちは、世界"}),
                "source_language": (languages, {"default": "auto_detect"}),
                "target_language": (
                    languages[1:],
                    {"default": "en"},  # exclude auto_detect
                ),
                "model_size": (["418M", "1.2B"], {"default": "418M"}),
                "device": (["auto", "cpu", "cuda"], {"default": "auto"}),
            },
            "optional": {
                "num_beams": ("INT", {"default": 5, "min": 1, "max": 10, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("translated_text", "detected_language", "confidence")

    FUNCTION = "translate"
    CATEGORY = "🌍 Translation/M2M-100"

    def ensure_model_downloaded(self, model_size) -> str:
        """Download the model in advance and return the local path"""
        model_name = MODEL_CONFIGS[model_size]["model_name"]
        cache_path = os.path.join(
            self.base_cache_dir,
            MODEL_CONFIGS[model_size]["cache_dir"],
        )

        # Check if the model is already downloaded
        if os.path.exists(cache_path) and os.listdir(cache_path):
            print(f"Model {model_size} already exists at {cache_path}")
            return cache_path

        # Download the model
        print(f"Downloading M2M-100 {model_size} model to {cache_path}...")
        downloaded_path = snapshot_download(
            repo_id=model_name,
            local_dir=cache_path,
            local_dir_use_symlinks=False,  # Copy actual files without using symbolic links
        )
        print(f"Model downloaded to {downloaded_path}")
        return cache_path

    def load_model(self, model_size, device) -> None:
        """Lazy load the model (first time only)"""
        model_name = MODEL_CONFIGS[model_size]["model_name"]

        # Determine device
        if device == "auto":
            actual_device = "cuda" if torch.cuda.is_available() else "cpu"
        elif device == "cuda":
            if not torch.cuda.is_available():
                print("Warning: CUDA is not available, falling back to CPU")
                actual_device = "cpu"
            else:
                actual_device = "cuda"
        else:
            actual_device = "cpu"

        # Do nothing if the model and device combination is already loaded
        model_key = f"{model_name}_{actual_device}"
        if self._model is not None and self._current_model_name == model_key:
            return

        # Download the model in advance
        local_model_path = self.ensure_model_downloaded(model_size)

        # Model loading process
        print(
            f"Loading M2M-100 {model_size} model from {local_model_path} on {actual_device}..."
        )

        if actual_device == "cuda":
            self._model = M2M100ForConditionalGeneration.from_pretrained(
                local_model_path,  # specify local path
                torch_dtype=torch.float16,
                device_map="auto",
            ).cuda()
        else:
            self._model = M2M100ForConditionalGeneration.from_pretrained(
                local_model_path,  # specify local path
                torch_dtype=torch.float32,
            )

        self._tokenizer = M2M100Tokenizer.from_pretrained(
            local_model_path,  # specify local path
        )
        self._current_model_name = model_key
        self.current_device = actual_device
        print(f"Model loaded successfully on {actual_device}!")

    def detect_language(self, text) -> tuple[str, float]:
        """Automatically detect language"""
        lang_code, confidence = langid.classify(text)
        return lang_code, confidence

    def translate(
        self,
        text,
        source_language,
        target_language,
        model_size,
        device,
        num_beams=5,
    ):
        """Translation"""
        # Return as is if text is empty
        if not text or text.strip() == "":
            return (
                text,
                source_language if source_language != "auto_detect" else "unknown",
                1.0,
            )

        # Automatic language detection
        if source_language == "auto_detect":
            source_language, confidence = self.detect_language(text)
            print(
                f"Detected language: {source_language} (confidence: {confidence:.2f})"
            )
        else:
            confidence = 1.0

        # Return as is if same language
        if source_language == target_language:
            return (text, source_language, confidence)

        # Execute translation
        self.load_model(model_size, device)
        self._tokenizer.src_lang = source_language
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self.current_device)
        with torch.no_grad():
            generated_tokens = self._model.generate(
                **inputs,
                forced_bos_token_id=self._tokenizer.get_lang_id(target_language),
                num_beams=num_beams,
                early_stopping=True,
                use_cache=True,
            )
        translated_texts = self._tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )[0]

        return (translated_texts, source_language, float(confidence))
