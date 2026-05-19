import re
import pymorphy3
import nltk
from nltk.stem import WordNetLemmatizer

# Download NLTK data (runs once, then cached)
try:
    nltk.download("wordnet", quiet=True, raise_on_error=True)
except Exception:
    # Fallback to standard offline download if any issues
    try:
        nltk.download("wordnet", quiet=True)
    except Exception:
        pass

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


# ─── Semantic Categories (Substring/Stem matching) ────────────────
EMOJI_CATEGORIES_EN = {
    "🥩": ["beef", "pork", "lamb", "meat", "mince", "steak", "sausage", "ham", "bacon", "chicken", "turkey", "poultry", "filet"],
    "🥛": ["milk", "kefir", "yogurt", "cream", "cheese", "curd"],
    "🍞": ["bread", "loaf", "bun", "baguette", "croissant", "dough", "pastry", "pie"],
    "🧀": ["cheese", "parmesan", "mozzarella", "cheddar", "gouda", "brie", "camembert"],
    "🥚": ["egg", "yolk", "albumen"],
    "🐟": ["fish", "salmon", "trout", "herring", "mackerel", "tuna", "caviar", "shrimp", "squid", "crab", "mussel", "seafood"],
    "🥔": ["potato", "mash"],
    "🧅": ["onion", "garlic", "leek"],
    "🍅": ["tomato", "ketchup", "paste"],
    "🥒": ["cucumber", "zucchini", "eggplant"],
    "🥬": ["cabbage", "salad", "spinach", "dill", "parsley", "cilantro", "basil", "greens", "lettuce"],
    "🥕": ["carrot", "beet", "radish", "turnip"],
    "🍎": ["apple", "pear", "plum", "peach", "apricot", "nectarine"],
    "🍊": ["orange", "mandarin", "lemon", "grapefruit", "lime", "citrus", "tangerine"],
    "🍌": ["banana"],
    "🍉": ["watermelon", "melon"],
    "🍓": ["strawberry", "raspberry", "blackberry", "blueberry", "currant", "cherry", "berry"],
    "🍇": ["grape", "raisin"],
    "🧈": ["butter", "margarine", "spread"],
    "💧": ["water", "aqua"],
    "🧃": ["juice", "nectar", "compote", "drink", "beverage"],
    "🍺": ["beer", "ale", "cider"],
    "🍷": ["wine", "champagne", "cognac", "whiskey", "vodka", "rum", "gin", "liquor", "alcohol", "tequila"],
    "☕": ["coffee", "cappuccino", "latte", "espresso"],
    "🍵": ["tea", "matcha"],
    "🍫": ["chocolate", "cocoa"],
    "🍬": ["candy", "caramel", "lollipop", "marmalade", "marshmallow", "sweets"],
    "🍪": ["cookie", "biscuit", "waffle", "cracker"],
    "🎂": ["cake", "muffin", "roll", "dessert"],
    "🍦": ["ice cream", "sundae", "gelato"],
    "🍯": ["honey", "syrup", "jam"],
    "🍚": ["rice", "buckwheat", "oatmeal", "cereal", "porridge", "millet", "couscous"],
    "🍝": ["macaroni", "spaghetti", "noodle", "pasta"],
    "🥫": ["canned", "stew", "pate", "pea", "corn", "bean", "olive"],
    "🍕": ["pizza"],
    "🍔": ["burger", "hamburger", "cheeseburger"],
    "🥣": ["soup", "broth", "flake", "muesli"],
    "🧂": ["salt", "spice", "seasoning", "sauce", "mayonnaise"],
    "🌶️": ["pepper", "chili", "paprika"],
    "🍄": ["mushroom", "champignon"],
    "🥜": ["nut", "peanut", "almond", "hazelnut", "cashew", "pistachio", "seed"],
    "🧼": ["soap", "shampoo", "gel", "powder", "conditioner", "cleaner", "detergent"],
    "🧽": ["sponge", "washcloth", "rag"],
    "🧻": ["paper", "napkin", "tissue", "pad", "diaper", "toilet"],
    "🐶": ["dog", "cat", "pet", "animal"],
    "💊": ["pill", "medicine", "vitamin", "pharmacy", "ointment", "patch"],
    "💄": ["lipstick", "cosmetic", "cream", "lotion", "makeup", "shower", "bath"],
}

EMOJI_CATEGORIES_RU = {
    "🥩": ["говядин", "свинин", "баранин", "мяс", "фарш", "стейк", "колбас", "ветчин", "бекон", "сал", "печен", "куриц", "индейк", "птиц", "филе", "сосиск", "сардельк"],
    "🥛": ["молок", "кефир", "ряженк", "йогурт", "творог", "сметан", "сливк", "сырок", "айран"],
    "🍞": ["хлеб", "батон", "булк", "багет", "лаваш", "лепешк", "сухар", "круассан", "тесто", "пирог", "выпечк"],
    "🧀": ["сыр", "пармезан", "моцарелл", "чеддер", "гауд"],
    "🥚": ["яйц", "желток", "белок", "перепелин"],
    "🐟": ["рыб", "лосос", "форел", "сельдь", "скумбри", "тун", "шпрот", "икр", "креветк", "кальмар", "краб", "миди", "морепродукт"],
    "🥔": ["картоф", "пюр"],
    "🧅": ["лук", "чеснок"],
    "🍅": ["помидор", "томат", "кетчуп", "паст"],
    "🥒": ["огур", "кабачок", "цуккин", "баклажан"],
    "🥬": ["капуст", "салат", "шпинат", "укроп", "петрушк", "кинз", "базилик", "зелен"],
    "🥕": ["морков", "свекл", "редис", "реп"],
    "🍎": ["яблок", "груш", "слив", "персик", "абрикос", "нектарин"],
    "🍊": ["апельсин", "мандарин", "лимон", "грейпфрут", "лайм", "цитрус"],
    "🍌": ["банан"],
    "🍉": ["арбуз", "дын"],
    "🍓": ["клубник", "земляник", "малин", "ежевик", "черник", "смородин", "вишн", "черешн", "ягод"],
    "🍇": ["виноград", "изюм"],
    "🧈": ["масл", "маргарин", "спред"],
    "💧": ["вод", "акв"],
    "🧃": ["сок", "нектар", "морс", "компот", "напиток"],
    "🍺": ["пив", "эль", "сидр"],
    "🍷": ["вин", "шампанск", "коньяк", "виски", "водк", "ром", "джин", "ликер", "алкогол", "текил"],
    "☕": ["коф", "капучино", "латт", "эспрессо"],
    "🍵": ["чай", "матч", "пуэр"],
    "🍫": ["шоколад", "кака", "батончик"],
    "🍬": ["конфет", "карамел", "леден", "мармелад", "зефир", "пастил", "халв", "сладост"],
    "🍪": ["печень", "пряник", "вафл", "бисквит", "сушк"],
    "🎂": ["торт", "пирожн", "кекс", "рулет", "десерт"],
    "🍦": ["морожен", "пломбир", "эскимо"],
    "🍯": ["мед", "сироп", "джем", "варень", "повидл"],
    "🍚": ["рис", "гречк", "овсянк", "круп", "каш", "пшен", "перловк", "кускус", "булгур"],
    "🍝": ["макарон", "спагетт", "лапш", "вермишел", "паст"],
    "🥫": ["консерв", "тушенк", "паштет", "горошек", "кукуруз", "фасол", "оливк", "маслин", "шпрот"],
    "🍕": ["пицц"],
    "🍔": ["бургер", "гамбургер", "чизбургер"],
    "🥣": ["суп", "бульон", "хлопь", "мюсл"],
    "🧂": ["соль", "приправ", "специ", "соус", "майонез", "горчиц"],
    "🌶️": ["перец", "чили", "паприк"],
    "🍄": ["гриб", "шампиньон", "лисичк", "опят"],
    "🥜": ["орех", "арахис", "миндал", "фундук", "кешью", "фисташк", "семечки"],
    "🧼": ["мыл", "шампун", "гель", "порошок", "кондиционер", "чистящ", "моюще"],
    "🧽": ["губк", "мочалк", "тряпк"],
    "🧻": ["бумаг", "салфетк", "платочк", "прокладк", "памперс", "подгузник", "туалетн"],
    "🐶": ["корм", "собак", "кошк", "кошач", "собач", "животн", "пес", "кот"],
    "💊": ["таблетк", "лек", "витамин", "аптек", "сироп", "мазь", "пластыр"],
    "💄": ["помад", "косметик", "крем", "лосьон", "макияж", "душ"],
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
    category_mapping = EMOJI_CATEGORIES_EN if lang != "ru" else EMOJI_CATEGORIES_RU
    words = lemma.split()

    # 1. Exact dictionary match (fastest, most precise)
    for word in reversed(words):
        if word in emoji_dict:
            return emoji_dict[word]

    # 2. Semantic category substring/stem match
    for word in reversed(words):
        for emoji, keywords in category_mapping.items():
            if any(kw in word for kw in keywords):
                return emoji

    return "📦"  # Default fallback emoji
