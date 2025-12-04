import streamlit as st
import pandas as pd
import time

# On essaie d'importer vos modules
try:
    from donnees import get_market_data, add_indicators, calculate_fibonacci
    from intelligence import generate_ai_analysis
    from backtest import FibonacciBacktester, plot_backtest_results
except ImportError as e:
    st.error(f"❌ Erreur d'importation : {e}")
    st.stop()

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Robot Trading IA",
    page_icon="🤖",
    layout="wide"
)

# --- TÊTE DE PAGE ---
st.title("🤖 Système de Trading Algorithmique Hybride")
st.markdown("**Stratégie :** Analyse Fibonacci + Validation IA Générative")
st.markdown("---")

# --- BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.header("⚙️ Configuration")
choix_actif = st.sidebar.radio(
    "Choisir le marché :",
    ("OR (Gold)", "NASDAQ (Tech)")
)

# Mapping du choix vers le symbole Yahoo Finance
ticker = "GC=F" if choix_actif == "OR (Gold)" else "^NDX"

st.sidebar.info(f"Symbole actif : **{ticker}**")
st.sidebar.markdown("---")
st.sidebar.write("👤 **Membres du groupe :**")
st.sidebar.write("- Étudiante 1 (Data)")
st.sidebar.write("- Étudiante 2 (IA)")
st.sidebar.write("- Étudiante 3 (Backtest)")

# --- 1. CHARGEMENT DES DONNÉES ---
@st.cache_data # Pour ne pas recharger à chaque clic
def charger_donnees(symbol):
    df = get_market_data(symbol)
    df = add_indicators(df)
    return df

with st.spinner(f'Téléchargement des données pour {choix_actif}...'):
    df = charger_donnees(ticker)
    fibs, high, low, trend = calculate_fibonacci(df)

# Affichage des métriques en haut
last_price = df['Close'].iloc[-1]
last_rsi = df['RSI'].iloc[-1]
tendance_icon = "📈" if trend == "up" else "📉"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Prix Actuel", f"${last_price:.2f}")
col2.metric("Tendance", f"{trend.upper()} {tendance_icon}")
col3.metric("RSI (14)", f"{last_rsi:.2f}")
col4.metric("Niveau Fib Clé", "61.8%")

# --- 2. INTELLIGENCE ARTIFICIELLE ---
st.header("🧠 Analyse de l'Intelligence Artificielle")

col_ia_1, col_ia_2 = st.columns([1, 2])

with col_ia_1:
    st.info("L'IA va analyser la confluence entre les niveaux Fibonacci, le RSI et le MACD pour donner une décision.")
    bouton_ia = st.button("✨ GÉNÉRER L'ANALYSE IA", use_container_width=True)

with col_ia_2:
    if bouton_ia:
        with st.spinner("L'IA réfléchit..."):
            # Préparation des données MACD
            macd_line = df.iloc[-1, -2]
            macd_signal = df.iloc[-1, -1]
            
            # Appel à votre fonction IA
            resultat = generate_ai_analysis(
                last_price, last_rsi, macd_line, macd_signal, fibs, trend, market=choix_actif
            )
            
            # Affichage joli du résultat
            if isinstance(resultat, dict):
                signal = resultat.get('signal', 'N/A')
                texte = resultat.get('analysis', '')
                
                if "ACHAT" in signal:
                    st.success(f"### SIGNAL : {signal}")
                elif "VENTE" in signal:
                    st.error(f"### SIGNAL : {signal}")
                else:
                    st.warning(f"### SIGNAL : {signal}")
                
                st.write(texte)
            else:
                st.write(resultat)

st.markdown("---")

# --- 3. BACKTEST & PERFORMANCE ---
st.header("📊 Performance Historique (Backtest)")

st.write("Simulation de la stratégie sur les données passées avec Stop Loss (2%) et Take Profit (5%).")

if st.button("🚀 LANCER LE BACKTEST"):
    with st.spinner("Simulation des trades en cours..."):
        # Initialisation du testeur (Code Étudiante 3)
        tester = FibonacciBacktester(df, initial_capital=10000)
        tester.generate_signals(calculate_fibonacci, lookback=50)
        tester.run_backtest(stop_loss_pct=2.0, take_profit_pct=5.0)
        metrics = tester.get_metrics()
        
        # Affichage des gros chiffres (Métriques)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Win Rate", f"{metrics['win_rate']}%")
        m2.metric("Profit Total", f"{metrics['total_return']}%")
        m3.metric("Profit Factor", f"{metrics['profit_factor']}")
        m4.metric("Trades Total", f"{metrics['total_trades']}")
        
        # Affichage du graphique interactif
        st.subheader("Graphique des Trades")
        fig = plot_backtest_results(tester.df, tester.trades, market=choix_actif)
        st.plotly_chart(fig, use_container_width=True)
        
        # Conclusion automatique
        if metrics['win_rate'] > 50:
            st.balloons()
            st.success("✅ La stratégie est rentable sur la période testée !")
        else:
            st.warning("⚠️ La stratégie nécessite des ajustements (Win Rate < 50%).")
