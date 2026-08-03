#!/usr/bin/env python3
"""
PROJECT KOLEKI — Multi-Asset Market Oracle
by: l3xtr
"""

import os
import sys
import time
import requests
from datetime import datetime

# ==================== WORKERS ====================
from workers.gatherer import Gatherer
from workers.researcher import Researcher
from workers.news_checker import NewsChecker
from workers.influencer import InfluencerTracker
from workers.flow_checker import FlowChecker
from workers.analysis import Analysis
from workers.predictor import Predictor
from workers.clarification import Clarification

# ==================== COLORS ====================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    BRIGHT_GREEN = "\033[38;5;46m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"
    PHOSPHOR = "\033[38;5;154m"
    DARK_GREEN = "\033[38;5;22m"

# ==================== ASCII ART ====================

BANNER = f"""
{C.BRIGHT_GREEN}
 ██╗  ██╗ ██████╗ ██╗     ███████╗██╗  ██╗██╗
 ██║ ██╔╝██╔═══██╗██║     ██╔════╝██║ ██╔╝██║
 █████╔╝ ██║   ██║██║     █████╗  █████╔╝ ██║
 ██╔═██╗ ██║   ██║██║     ██╔══╝  ██╔═██╗ ██║
 ██║  ██╗╚██████╔╝███████╗███████╗██║  ██╗██║
 ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝
{C.YELLOW}
           ╚══════════════════════════╝
{C.GRAY}           multi-asset market oracle{C.RESET}
{C.DIM}              by: l3xtr | v2.0{C.RESET}
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def divider(char="─", width=60):
    print(f"{C.DIM}{char * width}{C.RESET}")

def prompt(text):
    return input(f"{C.BRIGHT_GREEN}▶ {text}{C.RESET} ").strip()

# ==================== CURRENCY ====================

def get_php_rate():
    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        return resp.json()['rates']['PHP']
    except:
        return 56.50

def format_price_usd_php(usd_price, php_rate):
    php_price = usd_price * php_rate
    if usd_price >= 1:
        return f"${usd_price:,.2f} USD  (₱{php_price:,.2f} PHP)"
    elif usd_price >= 0.01:
        return f"${usd_price:.4f} USD  (₱{php_price:.4f} PHP)"
    else:
        return f"${usd_price:.8f} USD  (₱{php_price:.6f} PHP)"

# ==================== MARKET REFERENCE ====================

def show_market_reference():
    """Show available market reference"""
    print(f"\n{C.DIM}┌─ AVAILABLE MARKETS {'─' * 29}┐{C.RESET}")
    print(f"{C.DIM}│{C.RESET} {C.YELLOW}CRYPTO:{C.RESET}    BTC  ETH  SOL  XRP  DOGE  ADA  LINK")
    print(f"{C.DIM}│{C.RESET}            DOT  SHIB  LTC  BCH  PEPE  WIF  BONK")
    print(f"{C.DIM}│{C.RESET} {C.YELLOW}STOCKS:{C.RESET}    AAPL  TSLA  NVDA  MSFT  GOOGL  AMZN")
    print(f"{C.DIM}│{C.RESET}            META  NFLX  OSCR  PLTR  SOFI  RIVN")
    print(f"{C.DIM}│{C.RESET} {C.YELLOW}FOREX:{C.RESET}     EUR/USD  GBP/USD  USD/JPY  AUD/USD")
    print(f"{C.DIM}│{C.RESET}            USD/CAD  NZD/USD  EUR/GBP")
    print(f"{C.DIM}└{'─' * 50}┘{C.RESET}")

# ==================== INPUT COLLECTION ====================

def collect_inputs():
    inputs = {}
    
    print(f"\n{C.GRAY}┌─ QUERY SETUP {'─' * 37}┐{C.RESET}")
    
    print(f"{C.GRAY}│{C.RESET} {C.DIM}Type 'view' to see available markets{C.RESET}")
    while True:
        ticker = prompt("TICKER  (BTC, NVDA, EUR/USD...)").upper().strip()
        
        if ticker == 'VIEW':
            show_market_reference()
            continue
        
        if ticker and len(ticker) >= 2:
            inputs['ticker'] = ticker
            break
        print(f"{C.RED}  [!] Invalid ticker — try again or type 'view'{C.RESET}")
    
    print(f"\n{C.GRAY}│{C.RESET} {C.DIM}MODE:{C.RESET}")
    print(f"{C.GRAY}│{C.RESET}  {C.DIM}[1] SCALPING   [2] DAY TRADE   [3] SWING   [4] LONG{C.RESET}")
    
    mode_map = {'1': 'SCALPING', '2': 'DAY TRADE', '3': 'SWING', '4': 'LONG TERM'}
    while True:
        mode_raw = prompt("MODE    (1-4)").strip()
        if mode_raw in mode_map:
            inputs['mode_raw'] = mode_raw
            inputs['mode'] = mode_map[mode_raw]
            break
        print(f"{C.RED}  [!] Enter 1, 2, 3, or 4{C.RESET}")
    
    while True:
        cap = prompt("CAPITAL (PHP)").strip()
        try:
            inputs['capital'] = float(cap) if cap else 2500
            if inputs['capital'] > 0:
                break
            print(f"{C.RED}  [!] Must be greater than 0{C.RESET}")
        except ValueError:
            print(f"{C.RED}  [!] Enter a valid number (e.g. 5000){C.RESET}")
    
    while True:
        lev = prompt("LEVERAGE (1x-125x)").strip()
        try:
            inputs['leverage'] = float(lev.replace('x', '')) if lev else 1
            if 1 <= inputs['leverage'] <= 125:
                break
            print(f"{C.RED}  [!] Enter between 1 and 125{C.RESET}")
        except ValueError:
            print(f"{C.RED}  [!] Enter a valid number (e.g. 10){C.RESET}")
    
    print(f"{C.GRAY}└{'─' * 50}┘{C.RESET}")
    
    return inputs

# ==================== DISPLAY VERDICT ====================

def display_verdict(verdict, inputs, research_data, analysis_data):
    print(f"\n{C.GRAY}╔{'═' * 60}╗{C.RESET}")
    print(f"{C.GRAY}║{C.RESET}  {C.BRIGHT_GREEN}⚖️  FINAL VERDICT{C.RESET}")
    print(f"{C.GRAY}╚{'═' * 60}╝{C.RESET}")
    
    ov = verdict['overall']
    ap = verdict['approach']
    br = verdict['breakdown']
    pos = verdict['position']
    
    direction_color = C.BRIGHT_GREEN if 'BULLISH' in ov['direction'] else C.RED if 'BEARISH' in ov['direction'] else C.YELLOW
    php_rate = get_php_rate()
    
    # ===== OVERALL =====
    print(f"\n{C.BOLD}▌ OVERALL CONCLUSION{C.RESET}")
    print(f"  Direction:   {direction_color}{ov['direction']}{C.RESET}")
    print(f"  Confidence:  {C.YELLOW}{ov['confidence']}%{C.RESET}")
    print(f"  {C.DIM}{ov['summary']}{C.RESET}")
    
    # ===== APPROACH =====
    print(f"\n{C.BOLD}▌ SUGGESTED APPROACH ({ap['mode']}){C.RESET}")
    if ap['entry'] > 0:
        print(f"  Entry:       {format_price_usd_php(ap['entry'], php_rate)}")
        print(f"  Target:      {format_price_usd_php(ap['target'], php_rate)}")
        print(f"  Stop:        {format_price_usd_php(ap['stop'], php_rate)}")
    else:
        print(f"  Entry:       {C.DIM}calculating...{C.RESET}")
        print(f"  Target:      {C.DIM}calculating...{C.RESET}")
        print(f"  Stop:        {C.DIM}calculating...{C.RESET}")
    print(f"  Timeframe:   {ap['timeframe']}")
    print(f"  R:R Ratio:   {ap['rr_ratio']}")
    
    # ===== SIGNAL BREAKDOWN =====
    print(f"\n{C.BOLD}▌ SIGNAL BREAKDOWN{C.RESET}")
    
    ana = br.get('analysis', {}).get('detail', 'N/A')
    ana_conf = analysis_data.get('confidence', 0)
    conf_bar = '█' * int(ana_conf * 10) + '░' * (10 - int(ana_conf * 10))
    print(f"  {'Analysis':<18} {ana}")
    print(f"  {'Confidence':<18} {C.YELLOW}[{conf_bar}] {ana_conf:.0%}{C.RESET}")
    
    flow_detail = br.get('flow', {}).get('detail', 'N/A')
    flow_icon = '⚠' if '⚠' in flow_detail else '✓'
    print(f"  {'Flow':<18} {flow_icon} {flow_detail}")
    
    news_detail = br.get('news', {}).get('detail', 'N/A')
    print(f"  {'News':<18} {news_detail}")
    
    inf_detail = br.get('influencer', {}).get('detail', 'N/A')
    print(f"  {'Influencer':<18} {inf_detail}")
    
    pred_detail = br.get('predictor', {}).get('detail', 'N/A')
    print(f"  {'Predictor':<18} {pred_detail}")
    
    conf_detail = br.get('confluence', {}).get('detail', 'N/A')
    print(f"  {'Confluence':<18} {conf_detail}")
    
    manip_detail = br.get('manipulation', {}).get('detail', 'N/A')
    manip_icon = '⚠' if 'detected' in manip_detail.lower() else '✓'
    print(f"  {'Manipulation':<18} {manip_icon} {manip_detail}")
    
    div_detail = br.get('divergence', {}).get('detail', 'N/A')
    div_icon = '⚡' if 'divergence' in div_detail.lower() and 'no' not in div_detail.lower() else '✓'
    print(f"  {'Divergence':<18} {div_icon} {div_detail}")
    
    # ===== MARKET CONTEXT =====
    timeframes = research_data.get('timeframes', {})
    regime = research_data.get('regime', {})
    volatility = research_data.get('volatility', {})
    
    if timeframes:
        print(f"\n{C.BOLD}▌ MARKET CONTEXT{C.RESET}")
        
        tf_line = []
        for tf in ['weekly', 'daily', '4h', '1h']:
            if tf in timeframes:
                t = timeframes[tf]
                icon = '▲' if t['trend'] == 'bullish' else '▼' if t['trend'] == 'bearish' else '◆'
                tf_line.append(f"{tf}:{icon}")
        print(f"  Timeframes:  {'  '.join(tf_line)}")
        
        if regime:
            reg = regime.get('regime', 'unknown').replace('_', ' ').upper()
            print(f"  Regime:      {reg} (ADX: {regime.get('adx_14', 'N/A')})")
        
        if volatility:
            vol_reg = volatility.get('volatility_regime', 'normal').upper()
            atr_pct = volatility.get('atr_percent', 0)
            print(f"  Volatility:  {vol_reg} (ATR: {atr_pct}%)")
    
    # ===== POSITION =====
    print(f"\n{C.BOLD}▌ POSITION (Capital: ₱{inputs['capital']:,.2f}){C.RESET}")
    
    user_lev = inputs['leverage']
    for lev, vals in pos.items():
        if not lev.replace('x', '').replace('.', '').isdigit():
            continue
        try:
            lev_float = float(lev.replace('x', ''))
        except ValueError:
            continue
        highlight = C.YELLOW if lev_float == user_lev else C.DIM
        marker = '◄' if lev_float == user_lev else ' '
        print(f"  {highlight}{lev:<6} Size: ₱{vals['position_size']:,.2f} | Stop: -₱{vals['stop_loss']:,.2f} | TP: +₱{vals['take_profit']:,.2f} {marker}{C.RESET}")
    
    if user_lev > 10:
        print(f"\n  {C.YELLOW}⚡ {user_lev}x leverage — tight risk management required{C.RESET}")
    
    # ===== WARNINGS =====
    warnings = []
    if 'BULLISH' in ov['direction'] and ov['confidence'] < 50:
        warnings.append('Low confidence bullish — consider waiting for confirmation')
    if 'BEARISH' in ov['direction'] and ov['confidence'] < 50:
        warnings.append('Low confidence bearish — avoid shorting into uncertainty')
    if volatility.get('volatility_regime') in ['explosive', 'high']:
        warnings.append("High volatility regime — reduce position size")
    
    if warnings:
        print(f"\n{C.BOLD}▌ RISK NOTES{C.RESET}")
        for w in warnings:
            print(f"  {C.YELLOW}⚠ {w}{C.RESET}")


# ==================== MAIN ====================

def main():
    clear_screen()
    print(BANNER)
    
    print(f"{C.GRAY}[*] Initializing oracle workers...{C.RESET}")
    time.sleep(0.4)
    print(f"{C.GRAY}[*] Syncing market modules...{C.RESET}")
    time.sleep(0.3)
    print(f"{C.GRAY}[*] Oracle ready.{C.RESET}")
    
    inputs = collect_inputs()
    
    # Summary
    print(f"\n{C.GRAY}╔{'═' * 45}╗{C.RESET}")
    print(f"{C.GRAY}║{C.RESET} {C.BRIGHT_GREEN}QUERY CONFIRMED{C.RESET}")
    print(f"{C.GRAY}║{C.RESET} {C.DIM}Ticker:{C.RESET}   {C.YELLOW}{inputs['ticker']}{C.RESET}")
    print(f"{C.GRAY}║{C.RESET} {C.DIM}Mode:{C.RESET}     {C.YELLOW}{inputs['mode']}{C.RESET}")
    print(f"{C.GRAY}║{C.RESET} {C.DIM}Capital:{C.RESET}  {C.YELLOW}₱{inputs['capital']:,.2f}{C.RESET}")
    print(f"{C.GRAY}║{C.RESET} {C.DIM}Leverage:{C.RESET} {C.YELLOW}{inputs['leverage']}x{C.RESET}")
    print(f"{C.GRAY}╚{'═' * 45}╝{C.RESET}")
    
    # ============ ORCHESTRATE WORKERS ============
    
    print(f"\n{C.GRAY}╔{'═' * 60}╗{C.RESET}")
    print(f"{C.GRAY}║{C.RESET}  {C.BRIGHT_GREEN}🔮 ORACLE PROCESSING — 8 Workers{C.RESET}")
    print(f"{C.GRAY}╚{'═' * 60}╝{C.RESET}")
    
    gatherer = Gatherer()
    raw_data = gatherer.run(inputs['ticker'], inputs['mode'])
    
    if raw_data is None:
        print(f"\n{C.RED}╔{'═' * 50}╗{C.RESET}")
        print(f"{C.RED}║{C.RESET}  {C.RED}✕ ASSET NOT FOUND{C.RESET}")
        print(f"{C.RED}║{C.RESET}  {C.DIM}'{inputs['ticker']}' doesn't exist on any supported exchange{C.RESET}")
        print(f"{C.RED}║{C.RESET}  {C.DIM}Check spelling or try a different ticker{C.RESET}")
        print(f"{C.RED}╚{'═' * 50}╝{C.RESET}\n")
        return
    
    researcher = Researcher()
    research_data = researcher.run(raw_data)
    
    news = NewsChecker()
    news_data = news.run(raw_data)
    
    influencer = InfluencerTracker()
    influencer_data = influencer.run(raw_data)
    
    flow = FlowChecker()
    flow_data = flow.run(raw_data)
    
    analysis = Analysis()
    analysis_data = analysis.run(research_data)
    
    predictor = Predictor()
    predictor_data = predictor.run(research_data, inputs['mode'])
    
    clarification = Clarification()
    
    all_reports = {
        'research': research_data,
        'news': news_data,
        'influencer': influencer_data,
        'flow': flow_data,
        'analysis': analysis_data,
        'predictor': predictor_data
    }
    
    verdict = clarification.run(all_reports, inputs)
    
    display_verdict(verdict, inputs, research_data, analysis_data)
    
    print(f"\n{C.GRAY}╔{'═' * 60}╗{C.RESET}")
    print(f"{C.GRAY}║{C.RESET}  {C.DIM}by: l3xtr  |  v2.0  |  project_koleki  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}{C.RESET}")
    print(f"{C.GRAY}╚{'═' * 60}╝{C.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}[!] Oracle shutdown.{C.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{C.RED}[!] Fatal error: {e}{C.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)