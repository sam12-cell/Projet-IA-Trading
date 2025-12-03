import os

# --- CONFIGURATION IA ---
# Si tu as une clé API OpenAI (payante), mets-la entre les guillemets.
# Sinon, laisse vide : le mode "MANUEL" s'activera pour te donner le texte à copier.
OPENAI_API_KEY = "" 

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None # Gestion d'erreur si la librairie n'est pas installée

def generate_ai_analysis(price, rsi, fib_levels, trend):
    """
    Fonction qui construit l'analyse.
    """
    # 1. Mise en forme des niveaux Fibonacci pour le texte
    fib_text = ""
    for level, value in fib_levels.items():
        fib_text += f"- {level}: {value:.2f}\n"

    # 2. Le "Prompt" (La consigne pour l'IA)
    prompt = f"""
    Agis comme un expert trader professionnel sur l'OR (Gold).
    
    CONTEXTE DU MARCHÉ :
    - Prix Actuel : {price:.2f}
    - Tendance : {trend}
    - RSI (14) : {rsi:.2f}
    
    NIVEAUX FIBONACCI (Supports/Résistances) :
    {fib_text}
    
    TA MISSION :
    1. Analyse la position du prix par rapport aux niveaux Fibonacci.
    2. Utilise le RSI pour valider (Surachat > 70, Survente < 30).
    3. Donne une décision claire : [ACHAT], [VENTE] ou [NEUTRE].
    4. Rédige une explication courte et percutante.
    """

    # 3. Mode Automatique ou Manuel
    if not OPENAI_API_KEY or not OpenAI:
        return f"""
        === MODE MANUEL (Copie ce texte dans ChatGPT) ===
        {prompt}
        =================================================
        """
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {e}"

# --- ZONE DE CONNECTION (Le lien avec l'Étudiante 1) ---
if _name_ == "_main_":
    print("--- TEST INTELLIGENCE (Connecté à l'Étudiante 1) ---")
    
    try:
        # C'est ici qu'on appelle le travail de l'Étudiante 1 !
        from donnees import get_market_data, add_indicators, calculate_fibonacci
        
        # On récupère les données
        print("Lecture des données de l'Étudiante 1...")
        df = get_market_data("GC=F") # On force l'Or ici
        df = add_indicators(df)
        fibs, _, _, trend = calculate_fibonacci(df)
        
        # On lance l'analyse
        last_price = df['Close'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        
        print("\n--- GÉNÉRATION DE L'ANALYSE ---")
        print(generate_ai_analysis(last_price, last_rsi, fibs, trend))
        
    except ImportError:
        print("Erreur : Impossible de trouver le fichier donnees.py")
        print("Vérifie que le fichier 'donnees.py' est bien dans le même dossier.")
