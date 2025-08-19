from dataclasses import dataclass
from typing import List


@dataclass
class OrderRange:
    """仕掛けレンジの設定を表すデータクラス"""
    start_price: int     # 開始価格（円）
    end_price: int       # 終了価格（円）
    order_amount: int    # 1発注ごとの金額（円）


@dataclass
class OrderEntry:
    """個別注文エントリーを表すデータクラス"""
    price: int           # 注文価格（円）
    amount: int          # 発注金額（円）
    margin: int          # 必要証拠金（円）


@dataclass
class RiskAnalysis:
    """リスク分析結果を表すデータクラス"""
    total_orders: int                # 総注文数
    total_amount: int               # 総発注金額（円）
    total_margin: int               # 総証拠金（円）
    order_list: List[OrderEntry]    # 注文一覧
    
    @property
    def average_price(self) -> float:
        """平均注文価格を計算"""
        if not self.order_list:
            return 0.0
        return sum(entry.price for entry in self.order_list) / len(self.order_list)
    
    @property
    def price_range(self) -> int:
        """価格レンジを計算"""
        if not self.order_list:
            return 0
        prices = [entry.price for entry in self.order_list]
        return max(prices) - min(prices)