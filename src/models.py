from dataclasses import dataclass
from typing import List

from .constants import DEFAULT_LOSS_CUT_WIDTH, DEFAULT_QUANTITY


@dataclass
class OrderRange:
    """仕掛けレンジの設定を表すデータクラス"""
    start_price: int     # 開始価格（円）
    end_price: int       # 終了価格（円）
    order_amount: int    # 値幅（円）
    quantity: float = DEFAULT_QUANTITY  # 取引数量（デフォルト: 0.1）
    current_price: int = 0  # 現在値（円）
    loss_cut_rate: int = 0  # ロスカットレート（円）
    loss_cut_width: int = DEFAULT_LOSS_CUT_WIDTH  # ロスカット幅（円、デフォルト: 2139）


@dataclass
class OrderEntry:
    """個別注文エントリーを表すデータクラス"""
    price: int               # 注文価格（円）
    amount: int              # 発注金額（円）
    quantity: float          # 取引数量
    required_margin: float   # 必要証拠金（円）
    optional_margin: float   # 任意証拠金（円）
    profit_loss: float       # 損益（円）


@dataclass
class RiskAnalysis:
    """リスク分析結果を表すデータクラス"""
    total_orders: int                # 総注文数
    total_amount: int               # 総発注金額（円）
    total_required_margin: float    # 総必要証拠金（円）
    total_optional_margin: float    # 総任意証拠金（円）
    total_margin: float             # 総証拠金（必要＋任意）（円）
    total_profit_loss: float        # 総損益（円）
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