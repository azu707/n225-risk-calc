from typing import List
from .models import RiskAnalysis, OrderEntry


class CurrencyFormatter:
    """通貨フォーマッティングユーティリティクラス"""
    
    @staticmethod
    def format_yen(amount) -> str:
        """
        数値を日本円のカンマ区切り形式でフォーマット
        
        Args:
            amount: 金額（整数または浮動小数点数）
            
        Returns:
            str: フォーマットされた金額文字列（例: "40,000円"）
        """
        if isinstance(amount, float):
            return f"{int(amount):,}円"
        return f"{amount:,}円"
    
    @staticmethod
    def format_profit_loss(amount: float) -> str:
        """
        損益を符号付きでフォーマット
        
        Args:
            amount: 損益金額（浮動小数点数）
            
        Returns:
            str: フォーマットされた損益文字列（例: "+1,000円", "-500円"）
        """
        formatted_amount = f"{int(amount):,}円"
        if amount > 0:
            return f"+{formatted_amount}"
        elif amount < 0:
            return formatted_amount
        else:
            return "±0円"
    
    @staticmethod
    def format_number(number: int) -> str:
        """
        整数値をカンマ区切り形式でフォーマット
        
        Args:
            number: 数値（整数）
            
        Returns:
            str: フォーマットされた数値文字列（例: "1,000"）
        """
        return f"{number:,}"


class ResultFormatter:
    """計算結果の表示フォーマッタークラス"""
    
    def __init__(self):
        self.currency_formatter = CurrencyFormatter()
    
    def format_order_entry(self, entry: OrderEntry, index: int) -> str:
        """
        個別注文エントリーをフォーマット
        
        Args:
            entry: 注文エントリー
            index: 注文番号（1から開始）
            
        Returns:
            str: フォーマットされた注文情報
        """
        return (f"注文{index:2d}: "
                f"価格 {self.currency_formatter.format_yen(entry.price)}, "
                f"金額 {self.currency_formatter.format_yen(entry.amount)}, "
                f"数量 {entry.quantity}, "
                f"証拠金 {self.currency_formatter.format_yen(entry.margin)}, "
                f"損益 {self.currency_formatter.format_profit_loss(entry.profit_loss)}")
    
    def format_summary(self, analysis: RiskAnalysis) -> str:
        """
        リスク分析結果のサマリーをフォーマット
        
        Args:
            analysis: リスク分析結果
            
        Returns:
            str: フォーマットされたサマリー情報
        """
        summary_lines = [
            "=== リスク分析サマリー ===",
            f"総注文数: {self.currency_formatter.format_number(analysis.total_orders)}件",
            f"総発注金額: {self.currency_formatter.format_yen(analysis.total_amount)}",
            f"総必要証拠金: {self.currency_formatter.format_yen(analysis.total_required_margin)}",
            f"総任意証拠金: {self.currency_formatter.format_yen(analysis.total_optional_margin)}",
            f"総証拠金: {self.currency_formatter.format_yen(analysis.total_margin)}",
            f"総損益: {self.currency_formatter.format_profit_loss(analysis.total_profit_loss)}",
            f"平均注文価格: {self.currency_formatter.format_yen(int(analysis.average_price))}",
            f"価格レンジ: {self.currency_formatter.format_yen(analysis.price_range)}",
        ]
        return "\n".join(summary_lines)
    
    def format_order_list(self, order_list: List[OrderEntry]) -> str:
        """
        注文一覧をフォーマット
        
        Args:
            order_list: 注文エントリーのリスト
            
        Returns:
            str: フォーマットされた注文一覧
        """
        if not order_list:
            return "注文がありません。"
        
        lines = ["=== 注文一覧 ==="]
        for i, entry in enumerate(order_list, 1):
            lines.append(self.format_order_entry(entry, i))
        
        return "\n".join(lines)
    
    def format_full_analysis(self, analysis: RiskAnalysis) -> str:
        """
        完全なリスク分析結果をフォーマット
        
        Args:
            analysis: リスク分析結果
            
        Returns:
            str: フォーマットされた完全な分析結果
        """
        parts = [
            self.format_summary(analysis),
            "",
            self.format_order_list(analysis.order_list)
        ]
        return "\n".join(parts)
    
    def format_table_headers(self) -> List[str]:
        """
        テーブル表示用のヘッダーを取得
        
        Returns:
            List[str]: テーブルヘッダーのリスト
        """
        return ["注文番号", "注文価格", "発注金額", "取引数量", "必要証拠金", "任意証拠金", "損益"]
    
    def format_table_row(self, entry: OrderEntry, index: int) -> List[str]:
        """
        テーブル表示用の行データをフォーマット
        
        Args:
            entry: 注文エントリー
            index: 注文番号（1から開始）
            
        Returns:
            List[str]: テーブル行データのリスト
        """
        return [
            str(index),
            self.currency_formatter.format_yen(entry.price),
            self.currency_formatter.format_yen(entry.amount),
            str(entry.quantity),
            self.currency_formatter.format_yen(entry.required_margin),
            self.currency_formatter.format_yen(entry.optional_margin),
            self.currency_formatter.format_profit_loss(entry.profit_loss)
        ]