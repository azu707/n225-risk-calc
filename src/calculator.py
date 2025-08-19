from typing import List
from .models import OrderRange, OrderEntry, RiskAnalysis


class RiskCalculator:
    """日経225 CFDリスク計算エンジン"""
    
    def calculate_orders(self, order_range: OrderRange) -> RiskAnalysis:
        """
        指定されたレンジに基づいて注文を計算し、リスク分析を実行
        
        Args:
            order_range: 仕掛けレンジの設定
            
        Returns:
            RiskAnalysis: 計算結果とリスク分析
            
        Raises:
            ValueError: 不正な入力パラメータの場合
        """
        if order_range.start_price >= order_range.end_price:
            raise ValueError("開始価格は終了価格より小さい必要があります")
        
        if order_range.order_amount <= 0:
            raise ValueError("値幅は正の値である必要があります")
        
        if order_range.quantity < 0.1:
            raise ValueError("取引数量は0.1以上である必要があります")
        
        # 価格レンジを計算
        price_range = order_range.end_price - order_range.start_price
        
        # 値幅が価格レンジより大きい場合、1つの注文のみ
        if order_range.order_amount > price_range:
            order_entries = [
                OrderEntry(
                    price=order_range.start_price,
                    amount=order_range.order_amount,
                    quantity=order_range.quantity,
                    margin=order_range.start_price * order_range.quantity  # 証拠金は注文価格×取引数量
                )
            ]
        else:
            # 注文数を計算（端数は切り上げ）
            num_orders = (price_range + order_range.order_amount - 1) // order_range.order_amount
            
            # 各注文を生成
            order_entries = []
            for i in range(num_orders):
                order_price = order_range.start_price + (i * order_range.order_amount)
                # 終了価格を超えないように調整
                if order_price >= order_range.end_price:
                    break
                    
                order_entries.append(
                    OrderEntry(
                        price=order_price,
                        amount=order_range.order_amount,
                        quantity=order_range.quantity,
                        margin=order_price * order_range.quantity  # 証拠金は注文価格×取引数量
                    )
                )
        
        # 合計値を計算
        total_orders = len(order_entries)
        total_amount = sum(entry.amount for entry in order_entries)
        total_margin = sum(entry.margin for entry in order_entries)
        
        return RiskAnalysis(
            total_orders=total_orders,
            total_amount=total_amount,
            total_margin=total_margin,
            order_list=order_entries
        )
    
    def calculate_max_loss_scenario(self, analysis: RiskAnalysis, loss_per_point: int = 100) -> int:
        """
        最大損失シナリオを計算
        
        Args:
            analysis: リスク分析結果
            loss_per_point: 1ポイントあたりの損失額（デフォルト: 100円）
            
        Returns:
            int: 最大想定損失額（円）
        """
        if not analysis.order_list:
            return 0
        
        # 全てのポジションが最低価格まで下落したと仮定
        min_price = min(entry.price for entry in analysis.order_list)
        max_loss = 0
        
        for entry in analysis.order_list:
            # 各注文の価格から最低価格までの損失を計算
            price_diff = entry.price - min_price
            position_loss = price_diff * loss_per_point
            max_loss += position_loss
        
        return max_loss