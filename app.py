from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from transformers import MarianTokenizer
import nltk
import os
import re
import urllib.request
import urllib.error
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import pickle
import numpy as np
from keras.models import load_model
import json
import random
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector

# --- NLP Imports ---
from sentence_transformers import SentenceTransformer, util
from textblob import TextBlob

# --- NLTK Setup ---
# Only download if not present to speed up restart
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('popular')
    nltk.download('punkt_tab')

# WordNet is required by the lemmatizer and can fail under lazy-load race conditions.
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Force eager load once during startup to avoid first-request lazy loader issues.
wordnet.ensure_loaded()

lemmatizer = WordNetLemmatizer()

# --- Load Chatbot Model ---
model = load_model('model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('texts.pkl', 'rb'))
classes = pickle.load(open('labels.pkl', 'rb'))

# --- Spacy Language Detection ---
def get_lang_detector(nlp, name):
    return LanguageDetector()

# Load spacy model
nlp = spacy.load("en_core_web_sm")

# Register language detector (Check if already registered to avoid reload errors)
if not Language.has_factory("language_detector"):
    Language.factory("language_detector", func=get_lang_detector)
    nlp.add_pipe('language_detector', last=True)


# --- NLP: Sentence Transformer for Semantic Understanding ---
print("Loading Sentence Transformer model...")
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Build semantic search index from all patterns
print("Building semantic search index...")
pattern_to_intent = []  # List of (pattern, intent_tag) tuples
all_patterns = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        if pattern.strip():  # Skip empty patterns
            pattern_to_intent.append((pattern, intent['tag']))
            all_patterns.append(pattern)

# Encode all patterns into embeddings
pattern_embeddings = sentence_model.encode(all_patterns, convert_to_tensor=True)
print(f"Indexed {len(all_patterns)} patterns for semantic search")


def analyze_sentiment(text):
    """Analyze the sentiment of the text using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1
    subjectivity = blob.sentiment.subjectivity  # 0 to 1
    
    if polarity < -0.3:
        sentiment = "negative"
    elif polarity > 0.3:
        sentiment = "positive"
    else:
        sentiment = "neutral"
    
    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "sentiment": sentiment
    }


def extract_entities(text):
    """Extract named entities using spaCy"""
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "description": spacy.explain(ent.label_)
        })
    return entities


def semantic_search(query, top_k=3):
    """Find the most semantically similar patterns using sentence embeddings"""
    query_embedding = sentence_model.encode(query, convert_to_tensor=True)
    
    # Calculate cosine similarity
    similarities = util.cos_sim(query_embedding, pattern_embeddings)[0]
    
    # Get top-k most similar patterns
    top_results = []
    top_indices = similarities.argsort(descending=True)[:top_k]
    
    for idx in top_indices:
        idx = idx.item()
        pattern, intent_tag = pattern_to_intent[idx]
        score = similarities[idx].item()
        top_results.append({
            "pattern": pattern,
            "intent": intent_tag,
            "score": score
        })
    
    return top_results


def get_nlp_prediction(sentence):
    """
    Hybrid prediction using both bag-of-words model and semantic search.
    Returns the best matching intent with confidence.
    """
    # Check for negation - important for handling "not ok", "don't feel good", etc.
    negation_words = ["not", "n't", "don't", "dont", "doesn't", "doesnt", "never", "no", "can't", "cant", "won't", "wont", "isn't", "isnt", "aren't", "arent", "wasn't", "wasnt", "weren't", "werent"]
    sentence_lower = sentence.lower()
    has_negation = any(neg in sentence_lower for neg in negation_words)
    
    # Positive feeling words that when negated should flip to sad
    positive_words = ["ok", "okay", "good", "fine", "great", "well", "happy", "alright"]
    has_positive_word = any(pos in sentence_lower for pos in positive_words)
    
    # 1. Get bag-of-words prediction
    bow_results = predict_class(sentence, model)
    
    # 2. Get semantic search results
    semantic_results = semantic_search(sentence, top_k=3)
    
    # 3. Combine results - semantic search gets priority for better understanding
    if semantic_results and semantic_results[0]['score'] > 0.5:
        # High semantic confidence - use semantic result
        best_intent = semantic_results[0]['intent']
        confidence = semantic_results[0]['score']
        method = "semantic"
    elif bow_results and float(bow_results[0]['probability']) > 0.3:
        # Decent bag-of-words confidence
        best_intent = bow_results[0]['intent']
        confidence = float(bow_results[0]['probability'])
        method = "bow"
    elif semantic_results:
        # Fall back to best semantic match
        best_intent = semantic_results[0]['intent']
        confidence = semantic_results[0]['score']
        method = "semantic_fallback"
    else:
        return None, 0, "none"
    
    # Handle negation: If user says "not ok", "don't feel good", etc., flip happy to sad
    if has_negation and has_positive_word and best_intent == "happy":
        best_intent = "sad"
        method = method + "_negation_corrected"
        print(f"  [Negation detected] Flipped intent from 'happy' to 'sad'")
    
    return best_intent, confidence, method


# --- TRANSLATION MODELS ---
from transformers import MarianMTModel

# 1. English to Swahili
eng_swa_tokenizer = MarianTokenizer.from_pretrained("Rogendo/en-sw")
eng_swa_model = MarianMTModel.from_pretrained("Rogendo/en-sw")

def translate_to_swahili(text):
    # Safe check: if text is empty, return empty
    if not text: return ""
    try:
        inputs = eng_swa_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        translated = eng_swa_model.generate(**inputs)
        return eng_swa_tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Translation Error (En->Sw): {e}")
        return text

# 2. Swahili to English
swa_eng_tokenizer = MarianTokenizer.from_pretrained("Rogendo/sw-en")
swa_eng_model = MarianMTModel.from_pretrained("Rogendo/sw-en")

def translate_to_english(text):
    if not text: return ""
    try:
        inputs = swa_eng_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        translated = swa_eng_model.generate(**inputs)
        return swa_eng_tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Translation Error (Sw->En): {e}")
        return text


# --- CHATBOT LOGIC ---

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.1  # Lowered threshold for better matching
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    if ints:
        tag = ints[0]['intent']
        confidence = float(ints[0]['probability'])
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        # If confidence is low, add a soft prompt for clarification
        if confidence < 0.3:
            result = result + " (If this doesn't address your concern, please tell me more about how you're feeling.)"
        return result
    else:
        return "I'm not sure I fully understand. Could you tell me more about how you're feeling or what's on your mind?"


def get_response_by_intent(intent_tag, intents_json):
    """Get a response for a given intent tag"""
    for intent in intents_json['intents']:
        if intent['tag'] == intent_tag:
            return random.choice(intent['responses'])
    return None


def generate_nlp_response(user_text, sentiment_info):
    """
    Generate a response using NLP-enhanced understanding.
    Combines semantic search, sentiment analysis, and entity recognition.
    """
    # Get hybrid NLP prediction
    best_intent, confidence, method = get_nlp_prediction(user_text)
    
    print(f"  NLP Method: {method}, Intent: {best_intent}, Confidence: {confidence:.3f}")
    print(f"  Sentiment: {sentiment_info['sentiment']} (polarity: {sentiment_info['polarity']:.2f})")
    
    # Extract entities for context
    entities = extract_entities(user_text)
    if entities:
        print(f"  Entities: {[e['text'] + ' (' + e['label'] + ')' for e in entities]}")
    
    # Get base response
    if best_intent and confidence > 0.25:
        response = get_response_by_intent(best_intent, intents)
        
        if response:
            # Enhance response based on sentiment
            if sentiment_info['sentiment'] == 'negative' and sentiment_info['polarity'] < -0.5:
                # User seems very distressed
                empathy_prefixes = [
                    "I can sense you're going through a difficult time. ",
                    "I hear that you're struggling. ",
                    "I understand this is hard for you. "
                ]
                response = random.choice(empathy_prefixes) + response
            
            # Add confidence note for lower confidence matches
            if confidence < 0.4:
                response += " Feel free to tell me more if I didn't fully address your concern."
            
            return response
    
    # Fallback response with sentiment awareness
    if sentiment_info['sentiment'] == 'negative':
        return "I can tell something is troubling you. I'm here to listen. Could you tell me more about what's on your mind?"
    elif sentiment_info['sentiment'] == 'positive':
        return "That's great to hear! Is there anything specific you'd like to talk about today?"
    else:
        return "I'm here to help. Could you tell me more about what you'd like to discuss?"


# --- LLM CONFIGURATION (OLLAMA) ---
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct")
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
OLLAMA_TAGS_URL = os.getenv("OLLAMA_TAGS_URL", "http://localhost:11434/api/tags")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.5"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
DEFAULT_RESPONSE_STYLE = os.getenv("RESPONSE_STYLE", "balanced").strip().lower()

MENTAL_HEALTH_SYSTEM_PROMPT = (
    "You are a supportive mental-health assistant for educational and emotional support only. "
    "Use warm, non-judgmental language. Do not diagnose medical conditions, and do not claim to be a therapist or doctor. "
    "Provide practical coping steps (breathing, grounding, journaling, sleep hygiene, social support), and encourage professional help when symptoms persist or worsen. "
    "If user indicates self-harm, suicide, or immediate danger, prioritize safety: advise contacting local emergency services and a trusted person immediately. "
    "Keep answers concise, clear, and actionable."
)

STYLE_INSTRUCTIONS = {
    "balanced": "Give a warm, practical response in about 4-7 sentences with concrete next steps.",
    "concise": "Keep the response brief (2-4 sentences), direct, and practical.",
    "therapeutic": "Use a more reflective, validating tone and include 1-2 grounding or coping exercises."
}

CRISIS_PATTERNS = [
    # English phrases
    re.compile(r"\b(kill|hurt)\s+myself\b", re.IGNORECASE),
    re.compile(r"\b(end\s+my\s+life|want\s+to\s+die|commit\s+suicide)\b", re.IGNORECASE),
    re.compile(r"\b(no\s+reason\s+to\s+live|better\s+off\s+dead)\b", re.IGNORECASE),
    re.compile(r"\b(i\s+am\s+going\s+to\s+die|i\s+will\s+kill\s+myself)\b", re.IGNORECASE),
    # Swahili phrases
    re.compile(r"\bnataka\s+kufa\b", re.IGNORECASE),
    re.compile(r"\bnitajiua\b", re.IGNORECASE),
    re.compile(r"\bkujiua\b", re.IGNORECASE),
    re.compile(r"\bsiwezi\s+kuendelea\s+kuishi\b", re.IGNORECASE),
]


def get_style_instruction(style):
    """Return style instruction for prompt tuning."""
    normalized = (style or DEFAULT_RESPONSE_STYLE).strip().lower()
    return STYLE_INSTRUCTIONS.get(normalized, STYLE_INSTRUCTIONS["balanced"])


def contains_crisis_language(raw_text, processing_text):
    """Detect high-risk language using regex, multilingual phrases, and intent confidence."""
    text_candidates = [raw_text or "", processing_text or ""]

    # Regex and phrase detection across original + translated text.
    for text in text_candidates:
        for pattern in CRISIS_PATTERNS:
            if pattern.search(text):
                return True

    # Intent-based detection from existing classifier for additional safety coverage.
    intent, confidence, _ = get_nlp_prediction(processing_text or "")
    if intent == "suicide" and confidence >= 0.25:
        return True

    return False


def get_crisis_response():
    """Safety-first response for high-risk messages."""
    return (
        "I'm really glad you shared this. You deserve immediate support right now. "
        "If you might act on these thoughts, please call your local emergency number now and reach out to someone you trust who can stay with you. "
        "You can also contact a crisis hotline in your country right away. "
        "If you want, I can help you write a short message to ask for urgent help."
    )


def generate_llm_response(user_text, sentiment_info, response_style=None):
    """Generate response via Ollama chat API. Returns None on failure."""
    try:
        style_instruction = get_style_instruction(response_style)
        user_prompt = (
            f"User message: {user_text}\n"
            f"Detected sentiment: {sentiment_info['sentiment']} (polarity={sentiment_info['polarity']:.2f}).\n"
            f"Style instruction: {style_instruction}\n"
            "Respond with emotional support and practical next steps."
        )

        payload = {
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": MENTAL_HEALTH_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "options": {
                "temperature": LLM_TEMPERATURE,
                "top_p": LLM_TOP_P
            }
        }

        req = urllib.request.Request(
            OLLAMA_CHAT_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as response:
            response_text = response.read().decode("utf-8")
            response_data = json.loads(response_text)

        message = response_data.get("message", {})
        content = message.get("content", "").strip()
        return content or None

    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"LLM Error: {e}")
        return None


def check_ollama_status():
    """Check Ollama API reachability and whether configured model is available."""
    status = {
        "enabled": USE_LLM,
        "chat_url": OLLAMA_CHAT_URL,
        "tags_url": OLLAMA_TAGS_URL,
        "model": OLLAMA_MODEL,
        "service_reachable": False,
        "model_available": False,
        "error": None,
    }

    if not USE_LLM:
        return status

    try:
        req = urllib.request.Request(OLLAMA_TAGS_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            response_text = response.read().decode("utf-8")
            data = json.loads(response_text)

        models = data.get("models", [])
        names = [m.get("name", "") for m in models]
        status["service_reachable"] = True
        status["model_available"] = any(name.startswith(OLLAMA_MODEL) for name in names)
    except Exception as e:
        status["error"] = str(e)

    return status

# --- FLASK APP ---

app = Flask(__name__)
app.static_folder = 'static'
CORS(app)  # Enable CORS for all routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response_style = request.args.get('style', DEFAULT_RESPONSE_STYLE)

    if not userText:
        return "Please type a message so I can help."

    print(f"\n{'='*50}")
    print(f"Raw Input: {userText}")

    # 1. Detect Language
    doc = nlp(userText)
    detected_language = doc._.language['language']
    print(f"Detected Language: {detected_language}")

    # 2. Prepare text for processing (Must be English for the chatbot model)
    processing_text = userText
    
    # If user spoke Swahili, translate to English first
    if detected_language == 'sw':
        processing_text = translate_to_english(userText)
        print(f"Translated to English: {processing_text}")

    # 3. NLP Analysis
    sentiment_info = analyze_sentiment(processing_text)

    # 4. Safety gate + LLM/NLP response selection
    if contains_crisis_language(userText, processing_text):
        bot_response_en = get_crisis_response()
    else:
        bot_response_en = None

        if USE_LLM:
            bot_response_en = generate_llm_response(processing_text, sentiment_info, response_style)

        # Fall back to the existing NLP pipeline when LLM is disabled/unavailable.
        if not bot_response_en:
            bot_response_en = generate_nlp_response(processing_text, sentiment_info)

    print(f"Bot Response (En): {bot_response_en}")

    # 5. Final Output Processing
    final_response = bot_response_en

    # If user originally spoke Swahili, translate the answer back to Swahili
    if detected_language == 'sw':
        final_response = translate_to_swahili(bot_response_en)
        print(f"Translated Response (Sw): {final_response}")

    print(f"{'='*50}\n")
    return final_response


@app.route("/health")
def health_check():
    """Health endpoint for Flask + Ollama/model availability."""
    ollama_status = check_ollama_status()

    return jsonify({
        "status": "ok",
        "flask": {
            "up": True
        },
        "llm": {
            "enabled": ollama_status["enabled"],
            "service_reachable": ollama_status["service_reachable"],
            "model": ollama_status["model"],
            "model_available": ollama_status["model_available"],
            "chat_url": ollama_status["chat_url"],
            "tags_url": ollama_status["tags_url"],
            "error": ollama_status["error"]
        },
        "response_style": DEFAULT_RESPONSE_STYLE,
        "llm_temperature": LLM_TEMPERATURE,
        "llm_top_p": LLM_TOP_P
    })


@app.route("/analyze")
def analyze_text():
    """API endpoint to get NLP analysis of text"""
    userText = request.args.get('msg', '')
    if not userText:
        return json.dumps({"error": "No text provided"})
    
    # Perform NLP analysis
    sentiment = analyze_sentiment(userText)
    entities = extract_entities(userText)
    semantic_matches = semantic_search(userText, top_k=3)
    best_intent, confidence, method = get_nlp_prediction(userText)
    
    return json.dumps({
        "input": userText,
        "sentiment": sentiment,
        "entities": entities,
        "semantic_matches": semantic_matches,
        "predicted_intent": {
            "intent": best_intent,
            "confidence": confidence,
            "method": method
        }
    }, indent=2)


if __name__ == "__main__":
    app.run(debug=True)