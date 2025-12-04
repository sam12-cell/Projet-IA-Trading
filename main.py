# main.py - Fichier final pour lancer le projet

try:
    # On connecte les 3 parties du projet
    from donnees import get_market_data, add_indicators, calculate_fibonacci
    from intelligence import generate_ai_analysis
    from backtest import FibonacciBacktester, print_backtest_report
    print("Modules connectés avec succès.")
except ImportError as e:
    print(f"❌ Erreur : {e}")
    exit()

def lancer_le_robot():
    print("\n" + "="*60)
    print(" 🚀 DÉMARRAGE DU ROBOT DE TRADING (OR & IA)")
    print("="*60)

    # 1. DONNÉES
    print("\n[1/3] Récupération des données (OR)...")
    df = get_market_data("GC=F") 
    df = add_indicators(df)
    fibs, high, low, trend = calculate_fibonacci(df)
    print(f"   -> Données chargées. Tendance : {trend}")

    # 2. INTELLIGENCE ARTIFICIELLE
    print("\n[2/3] Analyse de l'IA en cours...")
    last_price = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    rapport = generate_ai_analysis(last_price, last_rsi, fibs, trend)
    print(rapport)

    # 3. BACKTEST (PERFORMANCE)
    print("\n[3/3] Vérification de la rentabilité...")
    tester = FibonacciBacktester(df, initial_capital=10000)
    tester.generate_signals(calculate_fibonacci, lookback=50)
    tester.run_backtest(stop_loss_pct=2.0, take_profit_pct=5.0)
    
    metrics = tester.get_metrics()
    print_backtest_report(metrics, tester.df, market="OR (Gold)")

if __name__ == "__main__":
    lancer_le_robot()
