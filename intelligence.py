import os
from datetime import datetime

# --- CONFIGURATION IA ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  OpenAI non installé. Mode MANUEL activé.")


# ============================================================================
# 1️⃣ CONSTRUCTION DU PROMPT (Le cerveau de l'IA)
# ============================================================================

def build_trading_prompt(price, rsi, macd_line, macd_signal, fib_levels, trend, market="OR"):
    """
    Construit un prompt professionnel pour l'IA.
    
    Args:
        price (float): Prix actuel
        rsi (float): Valeur RSI (0-100)
        macd_line (float): Ligne MACD
        macd_signal (float): Signal MACD
        fib_levels (dict): Niveaux Fibonacci
        trend (str): 'up' ou 'down'
        market (str): Nom du marché (OR, NASDAQ, etc.)
    
    Returns:
        str: Prompt formaté pour l'IA
    """
    
    # 📊 Formatage des niveaux Fibonacci
    fib_text = "\n".join([f"  • {level}: {value:.2f}" for level, value in fib_levels.items()])
    
    # 🎯 Analyse des indicateurs
    rsi_status = "SURACHAT ⚠️" if rsi > 70 else "SURVENTE ⚠️" if rsi < 30 else "NEUTRE ✅"
    macd_status = "HAUSSIER 📈" if macd_line > macd_signal else "BAISSIER 📉"
    
    prompt = f"""
🤖 ANALYSE TRADING PROFESSIONNEL - {market.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 DONNÉES ACTUELLES :
  • Prix : {price:.2f}
  • Tendance : {trend.upper()}
  • Date/Heure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 INDICATEURS TECHNIQUES :
  • RSI (14) : {rsi:.2f} → {rsi_status}
  • MACD : {macd_line:.4f}
  • Signal MACD : {macd_signal:.4f} → {macd_status}

📊 NIVEAUX FIBONACCI (Supports/Résistances) :
{fib_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 MISSION - Réponds EXACTEMENT comme suit :

1️⃣ SIGNAL : [ACHAT] / [VENTE] / [NEUTRE]

2️⃣ JUSTIFICATION : 
   - Analyse la position du prix vs Fibonacci
   - Valide avec RSI et MACD
   - 2-3 phrases maximum

3️⃣ POINTS CLÉS :
   - Stop Loss (prix où sortir en cas d'erreur)
   - Take Profit 1 (premier objectif)
   - Take Profit 2 (deuxième objectif)

4️⃣ CONFIANCE : Donne un score de 1-10 sur ta confiance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sois précis, chiffré et actionnable.
"""
    
    return prompt


# ============================================================================
# 2️⃣ APPEL À L'IA (OpenAI ou Mode Manuel)
# ============================================================================

def call_openai_api(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """
    Appelle l'API OpenAI avec gestion d'erreurs.
    
    Args:
        prompt (str): Le prompt à envoyer
        model (str): Modèle à utiliser
        temperature (float): Créativité (0=déterministe, 1=créatif)
    
    Returns:
        str: Réponse de l'IA ou message d'erreur
    """
    
    if not HAS_OPENAI:
        return "❌ OpenAI non installé. Utilise: pip install openai"
    
    if not OPENAI_API_KEY:
        return None  # Mode manuel
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert trader professionnel. Analyse les données et donne des décisions claires et chiffrées."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ Erreur API OpenAI : {str(e)}"


# ============================================================================
# 3️⃣ FONCTION PRINCIPALE (Génération de l'analyse)
# ============================================================================

def generate_ai_analysis(price, rsi, macd_line, macd_signal, fib_levels, trend, market="OR"):
    """
    Génère une analyse complète via l'IA.
    
    Args:
        price, rsi, macd_line, macd_signal, fib_levels, trend : Données de l'Étudiante 1
        market : Nom du marché
    
    Returns:
        dict : {
            'signal': 'ACHAT' / 'VENTE' / 'NEUTRE',
            'analysis': 'Texte complet',
            'prompt_used': 'Prompt utilisé',
            'mode': 'AUTO' ou 'MANUEL'
        }
    """
    
    # 🛠️ Construire le prompt
    prompt = build_trading_prompt(price, rsi, macd_line, macd_signal, fib_levels, trend, market)
    
    # 🤖 Appeler l'IA
    response = call_openai_api(prompt)
    
    if response is None:
        # Mode MANUEL
        return {
            'signal': 'MANUEL',
            'analysis': f"📋 COPIE CE TEXTE DANS ChatGPT:\n\n{prompt}",
            'prompt_used': prompt,
            'mode': 'MANUEL'
        }
    
    elif response.startswith("❌"):
        # Erreur
        return {
            'signal': 'ERREUR',
            'analysis': response,
            'prompt_used': prompt,
            'mode': 'ERREUR'
        }
    
    else:
        # Succès
        return {
            'signal': extract_signal_from_response(response),
            'analysis': response,
            'prompt_used': prompt,
            'mode': 'AUTO'
        }


# ============================================================================
# 4️⃣ EXTRACTION DU SIGNAL (Parser la réponse IA)
# ============================================================================

def extract_signal_from_response(response):
    """
    Extrait le signal [ACHAT]/[VENTE]/[NEUTRE] de la réponse IA.
    """
    response_upper = response.upper()
    
    if "[ACHAT]" in response_upper or "ACHAT" in response_upper[:100]:
        return "ACHAT 🟢"
    elif "[VENTE]" in response_upper or "VENTE" in response_upper[:100]:
        return "VENTE 🔴"
    else:
        return "NEUTRE 🟡"


# ============================================================================
# 5️⃣ EXPORT DU RAPPORT (Pour l'Étudiante 3)
# ============================================================================

def format_report(price, rsi, macd_line, macd_signal, fib_levels, trend, ai_response, market="OR"):
    """
    Formate un rapport complet pour le backtesting.
    
    Returns:
        dict : Données structurées pour l'Étudiante 3
    """
    
    return {
        'timestamp': datetime.now().isoformat(),
        'market': market,
        'price': price,
        'rsi': rsi,
        'macd_line': macd_line,
        'macd_signal': macd_signal,
        'trend': trend,
        'fibonacci_levels': fib_levels,
        'ai_signal': ai_response.get('signal', 'UNKNOWN'),
        'ai_analysis': ai_response.get('analysis', ''),
        'mode': ai_response.get('mode', 'UNKNOWN')
    }


# ============================================================================
# 6️⃣ ZONE DE TEST
# ============================================================================

if __name__ == "__main__":
    print("🧪 TEST IA_LOGIC.PY")
    print("=" * 60)
    
    # Données de test (simulation de ce que l'Étudiante 1 donne)
    test_data = {
        'price': 2050.25,
        'rsi': 65.42,
        'macd_line': 0.0342,
        'macd_signal': 0.0156,
        'fib_levels': {
            '23.6%': 2045.10,
            '38.2%': 2040.50,
            '50.0%': 2035.75,
            '61.8%': 2031.00,
            '100.0%': 2020.00,
        },
        'trend': 'up',
        'market': 'OR'
    }
    
    # 📊 Générer l'analyse
    result = generate_ai_analysis(
        price=test_data['price'],
        rsi=test_data['rsi'],
        macd_line=test_data['macd_line'],
        macd_signal=test_data['macd_signal'],
        fib_levels=test_data['fib_levels'],
        trend=test_data['trend'],
        market=test_data['market']
    )
    
    print(f"\n🎯 SIGNAL : {result['signal']}")
    print(f"📝 MODE : {result['mode']}")
    print(f"\n📄 ANALYSE :\n{result['analysis']}")
    
    # 📊 Générer le rapport
    report = format_report(
        **test_data,
        ai_response=result
    )
    
    print(f"\n✅ Rapport généré pour l'Étudiante 3 :")
    print(f"   Signal : {report['ai_signal']}")
    print(f"   Timestamp : {report['timestamp']}")
