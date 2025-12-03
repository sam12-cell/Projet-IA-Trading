import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_market_data(ticker, period="1y", interval="1d"):
    """Récupère les données de l'OR (GC=F)"""
    print(f"--- Téléchargement des données pour {ticker} ---")
    df = yf.download(ticker, period=period, interval=interval)
    df = df.dropna()
    # Correction pour éviter les erreurs de format Yahoo Finance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

def add_indicators(df):
    """Ajoute RSI et MACD"""
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    return df

def calculate_fibonacci(df, lookback=50):
    """Calcule Fibonacci sur les 50 derniers jours"""
    recent_data = df.tail(lookback)
    high_price = recent_data['High'].max()
    low_price = recent_data['Low'].min()
    
    # On trouve la tendance
    date_high = recent_data['High'].idxmax()
    date_low = recent_data['Low'].idxmin()
    trend = 'down' if date_high > date_low else 'up'
    
    diff = high_price - low_price
    levels = {}
    ratios = [0.236, 0.382, 0.5, 0.618, 1.0, 1.618]
    
    if trend == 'up':
        for r in ratios:
            levels[f"{r*100}%"] = high_price - (diff * r)
    else:
        for r in ratios:
            levels[f"{r*100}%"] = low_price + (diff * r)
            
    return levels, high_price, low_price, trend

# --- PARTIE PRINCIPALE ---
if __name__ == "__main__":
  #on choisi l'or
    CHOIX_MARCHE = "GC=F" 
    
    data = get_market_data(CHOIX_MARCHE)
    data = add_indicators(data)
    fibs, h, l, t = calculate_fibonacci(data)
    
    print(f"\nAnalyse sur l'OR (Gold) terminée !")
    print(f"Prix Haut récent : {h}, Prix Bas récent : {l}")
    print("Niveaux Fibonacci :", fibs)
