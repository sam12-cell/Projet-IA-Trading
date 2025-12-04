import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json

# ============================================================================
# 1️⃣ CLASSE BACKTESTING
# ============================================================================

class FibonacciBacktester:
    """
    Simule les trades basés sur les signaux IA sur une période historique.
    """
    
    def __init__(self, df, initial_capital=10000, trade_size=0.95):
        """
        Args:
            df : DataFrame avec colonnes ['Close', 'High', 'Low', 'RSI', 'MACD', etc.]
            initial_capital : Capital de départ en $
            trade_size : % du capital à utiliser par trade (0.95 = 95%)
        """
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.trade_size = trade_size
        
        # Historique des trades
        self.trades = []
        self.portfolio_values = []
        self.entry_prices = []
        self.exit_prices = []
        
    def generate_signals(self, fib_levels_func, lookback=50):
        """
        Génère les signaux ACHAT/VENTE basés sur Fibonacci + RSI + MACD.
        
        Args:
            fib_levels_func : Fonction qui retourne (levels, h, l, trend)
            lookback : Nombre de jours pour calculer Fibonacci
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[:i+1].tail(lookback)
            
            # Récupérer Fibonacci
            try:
                fib_levels, h, l, trend = fib_levels_func(self.df.iloc[:i+1])
            except:
                signals.append('HOLD')
                continue
            
            # Données actuelles
            close = self.df['Close'].iloc[i]
            rsi = self.df['RSI'].iloc[i] if 'RSI' in self.df.columns else 50
            
            # Logique de signal
            signal = self._determine_signal(close, rsi, fib_levels, trend, h, l)
            signals.append(signal)
        
        # Padding pour les premiers jours
        signals = ['HOLD'] * lookback + signals
        self.df['SIGNAL'] = signals
        
        return self.df
    
    def _determine_signal(self, close, rsi, fib_levels, trend, high, low):
        """
        Détermine le signal [ACHAT], [VENTE], [HOLD] basé sur la logique.
        """
        # Extraire les niveaux clés
        fib_50 = fib_levels.get('50.0%', (high + low) / 2)
        fib_618 = fib_levels.get('61.8%', (high + low) / 2)
        fib_382 = fib_levels.get('38.2%', (high + low) / 2)
        
        # Logique ACHAT
        if trend == 'up':
            if close < fib_618 and rsi < 70 and rsi > 30:
                return 'ACHAT'
        
        # Logique VENTE
        if trend == 'down':
            if close > fib_382 and rsi > 30 and rsi < 70:
                return 'VENTE'
        
        return 'HOLD'
    
    def run_backtest(self, stop_loss_pct=2.0, take_profit_pct=5.0):
        """
        Exécute le backtest avec gestion Stop Loss et Take Profit.
        
        Args:
            stop_loss_pct : % de perte avant de sortir
            take_profit_pct : % de gain pour prendre profit
        """
        capital = self.initial_capital
        position = None  # {'entry_price': X, 'entry_idx': Y, 'type': 'LONG'}
        
        for i in range(len(self.df)):
            signal = self.df['SIGNAL'].iloc[i]
            close = self.df['Close'].iloc[i]
            date = self.df.index[i]
            
            # === GESTION DE POSITION EXISTANTE ===
            if position is not None:
                entry_price = position['entry_price']
                pnl_pct = ((close - entry_price) / entry_price) * 100
                
                # Stop Loss ?
                if pnl_pct < -stop_loss_pct:
                    self._close_trade(i, close, entry_price, 'STOP LOSS', date, capital)
                    capital = self.trades[-1]['exit_capital']
                    position = None
                
                # Take Profit ?
                elif pnl_pct > take_profit_pct:
                    self._close_trade(i, close, entry_price, 'TAKE PROFIT', date, capital)
                    capital = self.trades[-1]['exit_capital']
                    position = None
            
            # === OUVERTURE DE NOUVELLE POSITION ===
            if position is None and signal == 'ACHAT':
                qty = (capital * self.trade_size) / close
                position = {
                    'entry_price': close,
                    'entry_idx': i,
                    'type': 'LONG',
                    'qty': qty
                }
                self.entry_prices.append(close)
            
            # === VENTE À DÉCOUVERT (Optionnel) ===
            elif position is None and signal == 'VENTE':
                qty = (capital * self.trade_size) / close
                position = {
                    'entry_price': close,
                    'entry_idx': i,
                    'type': 'SHORT',
                    'qty': qty
                }
                self.entry_prices.append(close)
            
            # === MISE À JOUR CAPITAL ===
            if position is not None:
                unrealized_pnl = (close - position['entry_price']) * position['qty']
                self.portfolio_values.append(capital + unrealized_pnl)
            else:
                self.portfolio_values.append(capital)
        
        self.df['PORTFOLIO'] = self.portfolio_values
        return self
    
    def _close_trade(self, exit_idx, exit_price, entry_price, exit_reason, date, capital):
        """Enregistre la fermeture d'un trade."""
        pnl = (exit_price - entry_price) * ((capital * self.trade_size) / entry_price)
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        new_capital = capital + pnl
        
        self.trades.append({
            'exit_idx': exit_idx,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': exit_reason,
            'date': date,
            'exit_capital': new_capital
        })
        
        self.exit_prices.append(exit_price)
    
    def get_metrics(self):
        """Calcule toutes les métriques de performance."""
        
        if len(self.trades) == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'total_return': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'risk_reward_ratio': 0
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        # Gains et pertes
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]
        
        # Win Rate
        win_rate = (len(wins) / len(trades_df)) * 100 if len(trades_df) > 0 else 0
        
        # Profit Factor (gains totaux / pertes totales en valeur absolue)
        total_wins = wins['pnl'].sum()
        total_losses = abs(losses['pnl'].sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Max Drawdown
        portfolio = np.array(self.portfolio_values)
        running_max = np.maximum.accumulate(portfolio)
        drawdown = (portfolio - running_max) / running_max
        max_drawdown = np.min(drawdown) * 100
        
        # Sharpe Ratio
        returns = np.diff(portfolio) / portfolio[:-1]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Return total
        total_return = ((self.portfolio_values[-1] - self.initial_capital) / self.initial_capital) * 100
        
        # Average Win/Loss
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0
        
        # Risk/Reward Ratio
        risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            'total_trades': len(trades_df),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'total_return': round(total_return, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'risk_reward_ratio': round(risk_reward, 2)
        }


# ============================================================================
# 2️⃣ VISUALISATION GRAPHIQUE
# ============================================================================

def plot_backtest_results(df, trades, market="OR"):
    """
    Crée un graphique interactif avec :
    - Prix + niveaux Fibonacci
    - Points d'entrée/sortie
    - Portfolio value
    - Indicateurs (RSI, MACD)
    """
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.5, 0.25, 0.25],
        specs=[[{"secondary_y": True}], [{}], [{}]]
    )
    
    # ========== ROW 1 : PRIX + FIBONACCI ==========
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'], name='Prix Close',
                   line=dict(color='blue', width=2)),
        row=1, col=1
    )
    
    # Points d'entrée (ACHAT)
    entries = df[df['SIGNAL'] == 'ACHAT']
    fig.add_trace(
        go.Scatter(x=entries.index, y=entries['Close'],
                   mode='markers', name='ACHAT 🟢',
                   marker=dict(size=10, color='green', symbol='triangle-up')),
        row=1, col=1
    )
    
    # Points de sortie (VENTE)
    exits = df[df['SIGNAL'] == 'VENTE']
    fig.add_trace(
        go.Scatter(x=exits.index, y=exits['Close'],
                   mode='markers', name='VENTE 🔴',
                   marker=dict(size=10, color='red', symbol='triangle-down')),
        row=1, col=1
    )
    
    # Portfolio Value (axe droit)
    if 'PORTFOLIO' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['PORTFOLIO'], name='Portfolio',
                       line=dict(color='purple', width=2, dash='dash')),
            row=1, col=1, secondary_y=True
        )
    
    # ========== ROW 2 : RSI ==========
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI (14)',
                       line=dict(color='orange', width=1.5),
                       fill='tozeroy'),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # ========== ROW 3 : MACD ==========
    if 'MACD_12_26_9' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_12_26_9'], name='MACD',
                       line=dict(color='cyan', width=1.5)),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACDh_12_26_9'], name='Signal MACD',
                       line=dict(color='magenta', width=1.5)),
            row=3, col=1
        )
    
    # ========== LAYOUT ==========
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Prix ($)", row=1, col=1)
    fig.update_yaxes(title_text="Portfolio ($)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    
    fig.update_layout(
        title=f"🎯 Backtest Fibonacci Trading - {market.upper()}",
        hovermode='x unified',
        height=1000,
        template='plotly_dark',
        showlegend=True
    )
    
    return fig


# ============================================================================
# 3️⃣ AFFICHAGE CONSOLE (RÉSUMÉ)
# ============================================================================

def print_backtest_report(metrics, df, market="OR"):
    """Affiche un rapport texte professionnel."""
    
    print("\n" + "="*70)
    print(f"📊 RAPPORT DE BACKTEST - {market.upper()}".center(70))
    print("="*70)
    
    print(f"\n⏰ Période : {df.index[0].strftime('%Y-%m-%d')} → {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"📈 Données : {len(df)} jours")
    
    print("\n" + "-"*70)
    print("🎯 MÉTRIQUES DE TRADING".center(70))
    print("-"*70)
    
    print(f"  Total de Trades          : {metrics['total_trades']}")
    print(f"  Win Rate (%)             : {metrics['win_rate']}%")
    print(f"  Profit Factor            : {metrics['profit_factor']}")
    print(f"  Gain Moyen               : ${metrics['avg_win']:.2f}")
    print(f"  Perte Moyenne            : ${metrics['avg_loss']:.2f}")
    print(f"  Ratio Risque/Récompense  : {metrics['risk_reward_ratio']:.2f}")
    
    print("\n" + "-"*70)
    print("💰 PERFORMANCE FINANCIÈRE".center(70))
    print("-"*70)
    
    print(f"  Retour Total (%)         : {metrics['total_return']}%")
    print(f"  Max Drawdown (%)         : {metrics['max_drawdown']}%")
    print(f"  Sharpe Ratio             : {metrics['sharpe_ratio']:.2f}")
    
    print("\n" + "="*70 + "\n")


# ============================================================================
# 4️⃣ ZONE DE TEST / INTÉGRATION
# ============================================================================

if __name__ == "__main__":
    print("🧪 TEST BACKTEST.PY")
    print("=" * 70)
    
    # Simulation : créer un DataFrame de test
    dates = pd.date_range(start='2024-01-01', periods=180, freq='D')
    prices = np.random.uniform(2000, 2100, 180)
    prices = np.cumsum(np.random.normal(0, 5, 180)) + 2050
    
    df_test = pd.DataFrame({
        'Close': prices,
        'High': prices + np.random.uniform(0, 10, 180),
        'Low': prices - np.random.uniform(0, 10, 180),
        'RSI': np.random.uniform(30, 70, 180),
        'MACD_12_26_9': np.random.uniform(-0.05, 0.05, 180),
        'MACDh_12_26_9': np.random.uniform(-0.02, 0.02, 180),
    }, index=dates)
    
    # Fonction Fibonacci de test
    def test_fibonacci(df):
        high = df['High'].max()
        low = df['Low'].min()
        diff = high - low
        return {
            '23.6%': low + (diff * 0.236),
            '38.2%': low + (diff * 0.382),
            '50.0%': low + (diff * 0.5),
            '61.8%': low + (diff * 0.618),
        }, high, low, 'up'
    
    # Lancer le backtest
    backtester = FibonacciBacktester(df_test, initial_capital=10000)
    backtester.generate_signals(test_fibonacci, lookback=50)
    backtester.run_backtest(stop_loss_pct=2.0, take_profit_pct=5.0)
    
    # Métriques
    metrics = backtester.get_metrics()
    print_backtest_report(metrics, backtester.df)
    
    # Graphique
    fig = plot_backtest_results(backtester.df, backtester.trades)
    fig.show()
