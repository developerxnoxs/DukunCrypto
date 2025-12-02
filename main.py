"""
AI Trading Analysis Bots - Main Entry Point

This module provides a unified entry point for running both trading analysis bots.
For production use, run each bot separately using the workflow commands.
"""

import argparse
import sys


def main():
    """Main entry point for the trading analysis bots."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Trading Analysis Bots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py btc     Run the BTC/Crypto Analyzer Bot
  python main.py forex   Run the Forex Analyzer Bot
  
For more information, see README.md
        """
    )
    
    parser.add_argument(
        "bot",
        choices=["btc", "forex"],
        nargs="?",
        help="Which bot to run: 'btc' for cryptocurrency, 'forex' for forex/commodities"
    )
    
    args = parser.parse_args()
    
    if args.bot is None:
        print("AI Trading Analysis Bots")
        print("=" * 40)
        print()
        print("Available bots:")
        print("  btc   - Cryptocurrency Analyzer (14 coins)")
        print("  forex - Forex & Commodities Analyzer (16 pairs)")
        print()
        print("Usage:")
        print("  python main.py btc     # Run crypto bot")
        print("  python main.py forex   # Run forex bot")
        print()
        print("Or run directly:")
        print("  python src/btc_analyzer.py")
        print("  python src/xau_analyzer.py")
        return
    
    if args.bot == "btc":
        print("Starting BTC/Crypto Analyzer Bot...")
        from src import btc_analyzer
    elif args.bot == "forex":
        print("Starting Forex Analyzer Bot...")
        from src import xau_analyzer


if __name__ == "__main__":
    main()
