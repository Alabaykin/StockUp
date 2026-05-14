import re
import pymorphy3
import nltk
from nltk.stem import WordNetLemmatizer

# Download NLTK data (runs once, then cached)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

morph_ru = pymorphy3.MorphAnalyzer()
lemmatizer_en = WordNetLemmatizer()

# ─── English emoji dictionary ───────────────────────────────────────
EMOJI_DICT_EN = {
    "milk": "🥛",
    "bread": "🍞",
    "apple": "🍏",
    "banana": "🍌",
    "cheese": "🧀",
    "egg": "🥚",
    "meat": "🥩",
    "fish": "🐟",
    "chicken": "🍗",
    "potato": "🥔",
    "carrot": "🥕",
    "onion": "🧅",
    "tomato": "🍅",
    "cucumber": "🥒",
    "butter": "🧈",
    "water": "💧",
    "juice": "🧃",
    "beer": "🍺",
    "wine": "🍷",
    "coffee": "☕",
    "tea": "🍵",
    "chocolate": "🍫",
    "cookie": "🍪",
    "cake": "🎂",
    "ice cream": "🍦",
    "watermelon": "🍉",
    "strawberry": "🍓",
    "cherry": "🍒",
    "lemon": "🍋",
    "orange": "🍊",
    "grape": "🍇",
    "rice": "🍚",
    "pasta": "🍝",
    "pizza": "🍕",
    "hamburger": "🍔",
    "sausage": "🌭",
    "soup": "🥣",
    "salad": "🥗",
    "popcorn": "🍿",
    "salt": "🧂",
    "pepper": "🌶️",
    "sugar": "🍚",
    "honey": "🍯",
    "mushroom": "🍄",
    "garlic": "🧄",
    "cabbage": "🥬",
    "broccoli": "🥦",
    "nut": "🥜",
    "soap": "🧼",
    "sponge": "🧽",
    "paper": "🧻",
    "avocado": "🥑",
    "corn": "🌽",
    "shrimp": "🦐",
    "lobster": "🦞",
    "bacon": "🥓",
    "sandwich": "🥪",
    "taco": "🌮",
    "burrito": "🌯",
    "croissant": "🥐",
    "pretzel": "🥨",
    "bagel": "🥯",
    "pancake": "🥞",
    "waffle": "🧇",
    "pie": "🥧",
    "donut": "🍩",
    "candy": "🍬",
    "lollipop": "🍭",
    "cupcake": "🧁",
    "peanut": "🥜",
    "coconut": "🥥",
    "peach": "🍑",
    "pear": "🍐",
    "mango": "🥭",
    "pineapple": "🍍",
    "kiwi": "🥝",
    "blueberry": "🫐",
    "olive": "🫒",
    "chili": "🌶️",
    "ginger": "🫚",
    "pea": "🫛",
}

# ─── Russian emoji dictionary ───────────────────────────────────────
EMOJI_DICT_RU = {
    "молоко": "🥛",
    "хлеб": "🍞",
    "яблоко": "🍏",
    "банан": "🍌",
    "сыр": "🧀",
    "яйцо": "🥚",
    "мясо": "🥩",
    "рыба": "🐟",
    "курица": "🍗",
    "картофель": "🥔",
    "морковь": "🥕",
    "лук": "🧅",
    "помидор": "🍅",
    "огурец": "🥒",
    "масло": "🧈",
    "вода": "💧",
    "сок": "🧃",
    "пиво": "🍺",
    "вино": "🍷",
    "кофе": "☕",
    "чай": "🍵",
    "шоколад": "🍫",
    "печенье": "🍪",
    "торт": "🎂",
    "мороженое": "🍦",
    "арбуз": "🍉",
    "клубника": "🍓",
    "вишня": "🍒",
    "лимон": "🍋",
    "апельсин": "🍊",
    "виноград": "🍇",
    "рис": "🍚",
    "макароны": "🍝",
    "пицца": "🍕",
    "гамбургер": "🍔",
    "сосиска": "🌭",
    "суп": "🥣",
    "салат": "🥗",
    "попкорн": "🍿",
    "соль": "🧂",
    "перец": "🌶️",
    "сахар": "🍚",
    "мед": "🍯",
    "гриб": "🍄",
    "чеснок": "🧄",
    "капуста": "🥬",
    "брокколи": "🥦",
    "орех": "🥜",
    "мыло": "🧼",
    "губка": "🧽",
    "бумага": "🧻",
}


def normalize_product_name(name: str, lang: str = "en") -> str:
    """Normalize a product name to its base form (lemma).
    
    Args:
        name: Raw product name (e.g. "Green apples" or "Зеленые яблоки").
        lang: Language code – "en" or "ru".
    """
    # Remove digits and extra whitespace
    cleaned = re.sub(r"\d+", "", name).strip()
    words = cleaned.lower().split()

    if lang == "ru":
        lemmas = [morph_ru.parse(w)[0].normal_form for w in words]
    else:
        # English: lemmatize as noun by default
        lemmas = [lemmatizer_en.lemmatize(w) for w in words]

    return " ".join(lemmas)


def get_emoji_for_product(lemma: str, lang: str = "en") -> str:
    """Pick an emoji based on the lemmatized product name.
    
    Args:
        lemma: Lemmatized product name.
        lang: Language code – "en" or "ru".
    """
    emoji_dict = EMOJI_DICT_EN if lang != "ru" else EMOJI_DICT_RU
    words = lemma.split()

    # Search from the end — the key noun is usually last
    for word in reversed(words):
        if word in emoji_dict:
            return emoji_dict[word]

    return "📦"  # Default emoji
