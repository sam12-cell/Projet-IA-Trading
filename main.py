# main.py - Lancement du Robot Trading IA

import sys

# 1. IMPORTATION DES MODULES
try:
    from donnees import get_market_data, add_indicators, calculate_fibonacci
    # Attention : Assure-toi que le fichier s'appelle bien intelligence.py
    from intelligence import generate_ai_analysis 
    from backtest import FibonacciBacktester, print_backtest_report, plot_backtest_results
    print("✅ Modules connectés avec succès.")
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("Vérifie que les fichiers donnees.py, intelligence.py et backtest.py existent.")
    sys.exit()

def demarrer_projet():
    print("\n" + "="*60)
    print(" 🚀 DÉMARRAGE DU SYSTÈME DE TRADING (OR & IA)")
    print("="*60)

    # --- PHASE 1 : DONNÉES (Étudiante 1) ---
    print("\n[1/3] Récupération des données (OR)...")
    df = get_market_data("GC=F") 
    df = add_indicators(df)
    
    # Calcul initial pour l'affichage
    fibs, high, low, trend = calculate_fibonacci(df)
    print(f"   -> Données chargées ({len(df)} jours).")
    print(f"   -> Tendance détectée : {trend.upper()}")

    # --- PHASE 2 : INTELLIGENCE ARTIFICIELLE (Étudiante 2) ---
    print("\n[2/3] Analyse de l'IA en cours...")
    
    # Préparation des données spécifiques pour ton code IA avancé
    last_price = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # On cherche les colonnes MACD (pandas_ta les nomme parfois bizarrement)
    # On prend les 2 dernières colonnes qui sont généralement MACD et Signal
    macd_line = df.iloc[-1, -2] 
    macd_signal = df.iloc[-1, -1] 

    # Appel au cerveau de l'IA
    resultat_ia = generate_ai_analysis(
        price=last_price,
        rsi=last_rsi,
        macd_line=macd_line,
        macd_signal=macd_signal,
        fib_levels=fibs,
        trend=trend,
        market="OR"
    )
    
    print("\n" + "-"*40)
    print(f" 🧠 SIGNAL IA : {resultat_ia['signal']}")
    print("-"*40)
    print(resultat_ia['analysis'])
    print("-" * 40)

    # --- PHASE 3 : BACKTEST (Étudiante 3) ---
    print("\n[3/3] Backtest et Validation...")
    
    # Initialisation de la classe de l'étudiante 3
    tester = FibonacciBacktester(df, initial_capital=10000)
    
    # Génération des signaux (On passe la fonction calculate_fibonacci)
    tester.generate_signals(calculate_fibonacci, lookback=50)
    
    # Lancement de la simulation
    tester.run_backtest(stop_loss_pct=2.0, take_profit_pct=5.0)
    
    # Affichage du rapport
    metrics = tester.get_metrics()
    print_backtest_report(metrics, tester.df, market="OR (Gold)")
    
    # Tentative d'affichage du graphique (fonctionne sur Colab)
    try:
        fig = plot_backtest_results(tester.df, tester.trades, market="OR")
        fig.show()
        print("✅ Graphique interactif généré.")
    except Exception as e:
        print(f"Note: Graphique non affiché ({e})")

    print("\n✅ FIN DU PROGRAMME.")

if __name__ == "__main__":
    demarrer_projet()
