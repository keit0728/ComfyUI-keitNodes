from typing import Any
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import langid
import os
import folder_paths

MODEL_CONFIGS = {
    "418M": {
        "model_name": "facebook/m2m100_418M",
        "cache_dir": "models--facebook--m2m100_418M",
    },
    "1.2B": {
        "model_name": "facebook/m2m100_1.2B",
        "cache_dir": "models--facebook--m2m100_1.2B",
    },
}


class M2MTranslator:
    """
    M2M-100多言語翻訳
    """

    # クラス変数でモデルを保持（複数ノードで共有）
    _model: M2M100ForConditionalGeneration | None = None
    _tokenizer: Any | None = None
    _current_model_name: str | None = None

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.base_cache_dir = os.path.join(folder_paths.models_dir, "keit-nodes")

    @classmethod
    def INPUT_TYPES(cls):
        # M2M-100でサポートする言語リスト（主要なものを抜粋）
        languages = [
            "auto_detect",
            "ja",  # 日本語
            "en",  # 英語
            "zh",  # 中国語
            "ko",  # 韓国語
            "fr",  # フランス語
            "de",  # ドイツ語
            "es",  # スペイン語
            "ru",  # ロシア語
            "ar",  # アラビア語
            "hi",  # ヒンディー語
            "pt",  # ポルトガル語
            "it",  # イタリア語
            "tr",  # トルコ語
            "th",  # タイ語
            "vi",  # ベトナム語
            "pl",  # ポーランド語
            "nl",  # オランダ語
            "sv",  # スウェーデン語
            "da",  # デンマーク語
            "no",  # ノルウェー語
            "fi",  # フィンランド語
            "cs",  # チェコ語
            "hu",  # ハンガリー語
            "ro",  # ルーマニア語
            "bg",  # ブルガリア語
            "hr",  # クロアチア語
            "sk",  # スロバキア語
            "sl",  # スロベニア語
            "et",  # エストニア語
            "lv",  # ラトビア語
            "lt",  # リトアニア語
            "uk",  # ウクライナ語
            "be",  # ベラルーシ語
            "mk",  # マケドニア語
            "sq",  # アルバニア語
            "sr",  # セルビア語
            "bs",  # ボスニア語
            "is",  # アイスランド語
            "ga",  # アイルランド語
            "cy",  # ウェールズ語
            "ca",  # カタルーニャ語
            "fa",  # ペルシア語
            "ur",  # ウルドゥー語
            "bn",  # ベンガル語
            "ta",  # タミル語
            "te",  # テルグ語
            "kn",  # カンナダ語
            "ml",  # マラヤーラム語
            "gu",  # グジャラート語
            "pa",  # パンジャーブ語
            "mr",  # マラーティー語
            "ne",  # ネパール語
            "si",  # シンハラ語
            "my",  # ビルマ語
            "km",  # クメール語
            "lo",  # ラオ語
            "ka",  # ジョージア語
            "hy",  # アルメニア語
            "az",  # アゼルバイジャン語
            "kk",  # カザフ語
            "uz",  # ウズベク語
            "mn",  # モンゴル語
            "he",  # ヘブライ語
            "yi",  # イディッシュ語
            "sw",  # スワヒリ語
            "zu",  # ズールー語
            "xh",  # コサ語
            "af",  # アフリカーンス語
            "am",  # アムハラ語
            "ha",  # ハウサ語
            "ig",  # イボ語
            "yo",  # ヨルバ語
            "so",  # ソマリ語
            "mg",  # マダガスカル語
            "id",  # インドネシア語
            "ms",  # マレー語
            "tl",  # タガログ語
            "jv",  # ジャワ語
            "su",  # スンダ語
            "ceb",  # セブアノ語
        ]

        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "こんにちは、世界"}),
                "source_language": (languages, {"default": "auto_detect"}),
                "target_language": (
                    languages[1:],
                    {"default": "en"},  # auto_detectを除外
                ),
                "model_size": (["418M", "1.2B"], {"default": "418M"}),
            },
            "optional": {
                "num_beams": ("INT", {"default": 5, "min": 1, "max": 10, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("translated_text", "detected_language", "confidence")

    FUNCTION = "translate"
    CATEGORY = "🌍 Translation/M2M-100"

    def load_model(self, model_size) -> None:
        """モデルを遅延ロード（初回のみ）"""
        model_name = MODEL_CONFIGS[model_size]["model_name"]
        cache_path = os.path.join(
            self.base_cache_dir, MODEL_CONFIGS[model_size]["cache_dir"]
        )

        # モデルが既にロードされている場合は何もしない
        if self._model is not None and self._current_model_name == model_name:
            return

        # モデルロード処理
        print(f"Loading M2M-100 {model_size} model...")

        if torch.cuda.is_available():
            self._model = M2M100ForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                cache_dir=cache_path,
            ).cuda()
        else:
            self._model = M2M100ForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                cache_dir=cache_path,
            )

        self._tokenizer = M2M100Tokenizer.from_pretrained(
            model_name,
            cache_dir=cache_path,
        )
        self._current_model_name = model_name
        print("Model loaded successfully!")

    def detect_language(self, text) -> tuple[str, float]:
        """言語を自動検出"""
        lang_code, confidence = langid.classify(text)
        return lang_code, confidence

    def translate(
        self,
        text,
        source_language,
        target_language,
        model_size,
        num_beams=5,
    ):
        """翻訳"""
        # 同じ言語の場合はそのまま返す
        if source_language == target_language:
            return (text, source_language, confidence)

        # 言語自動検出
        if source_language == "auto_detect":
            source_language, confidence = self.detect_language(text)
            print(
                f"Detected language: {source_language} (confidence: {confidence:.2f})"
            )
        else:
            confidence = 1.0

        # 翻訳実行
        self.load_model(model_size)
        self._tokenizer.src_lang = source_language
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self.device)
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
