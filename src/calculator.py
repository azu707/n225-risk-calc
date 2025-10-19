from typing import List
from .models import OrderRange, OrderEntry, RiskAnalysis
from .constants import ORDER_TYPE_BUY, ORDER_TYPE_SELL


class RiskCalculator:
    """日経225 CFDリスク計算エンジン"""

    # 日経225 CFDのレバレッジ倍率
    LEVERAGE = 10

    def _determine_order_type(self, order_range: OrderRange) -> str:
        """
        取引方向を判定

        Args:
            order_range: 仕掛けレンジの設定

        Returns:
            str: ORDER_TYPE_BUY または ORDER_TYPE_SELL
        """
        if order_range.order_type is not None:
            return order_range.order_type

        # 開始価格 < 終了価格なら買い上がり、それ以外は売り下がり
        return ORDER_TYPE_BUY if order_range.start_price < order_range.end_price else ORDER_TYPE_SELL

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
        # 取引方向を判定
        order_type = self._determine_order_type(order_range)

        # 基本的なバリデーション
        if order_range.start_price == order_range.end_price:
            raise ValueError("開始価格と終了価格は異なる値である必要があります")

        if order_range.order_amount <= 0:
            raise ValueError("値幅は正の値である必要があります")

        if order_range.quantity < 0.1:
            raise ValueError("取引数量は0.1以上である必要があります")

        if order_range.current_price <= 0:
            raise ValueError("現在値は正の値である必要があります")

        if order_range.loss_cut_rate <= 0:
            raise ValueError("ロスカットレートは正の値である必要があります")

        if order_range.loss_cut_width <= 0:
            raise ValueError("ロスカット幅は正の値である必要があります")

        # 価格レンジを計算（絶対値）
        price_range = abs(order_range.end_price - order_range.start_price)

        # 値幅が価格レンジより大きい場合、1つの注文のみ
        if order_range.order_amount > price_range:
            order_entries = [self._create_order_entry(
                order_range.start_price,
                order_range.order_amount,
                order_range.quantity,
                order_range.current_price,
                order_range.loss_cut_rate,
                order_range.loss_cut_width,
                order_type
            )]
        else:
            # 注文数を計算（端数は切り上げ）
            num_orders = (price_range + order_range.order_amount - 1) // order_range.order_amount

            # 各注文を生成
            order_entries = []
            for i in range(num_orders):
                if order_type == ORDER_TYPE_BUY:
                    # 買い上がり: 開始価格から上昇
                    order_price = order_range.start_price + (i * order_range.order_amount)
                    # 終了価格を超えないように調整
                    if order_price >= order_range.end_price:
                        break
                else:
                    # 売り下がり: 開始価格から下降
                    order_price = order_range.start_price - (i * order_range.order_amount)
                    # 終了価格を超えないように調整
                    if order_price <= order_range.end_price:
                        break

                order_entries.append(self._create_order_entry(
                    order_price,
                    order_range.order_amount,
                    order_range.quantity,
                    order_range.current_price,
                    order_range.loss_cut_rate,
                    order_range.loss_cut_width,
                    order_type
                ))

        # 合計値を計算
        total_orders = len(order_entries)
        total_amount = sum(entry.amount for entry in order_entries)
        total_required_margin = sum(entry.required_margin for entry in order_entries)
        total_optional_margin = sum(entry.optional_margin for entry in order_entries)
        total_margin = total_required_margin + total_optional_margin
        total_profit_loss = sum(entry.profit_loss for entry in order_entries)

        return RiskAnalysis(
            total_orders=total_orders,
            total_amount=total_amount,
            total_required_margin=total_required_margin,
            total_optional_margin=total_optional_margin,
            total_margin=total_margin,
            total_profit_loss=total_profit_loss,
            order_list=order_entries,
            order_type=order_type
        )

    def _create_order_entry(
        self,
        order_price: int,
        order_amount: int,
        quantity: float,
        current_price: int,
        loss_cut_rate: int,
        loss_cut_width: int,
        order_type: str
    ) -> OrderEntry:
        """
        個別注文エントリーを作成

        Args:
            order_price: 注文価格
            order_amount: 発注金額
            quantity: 取引数量
            current_price: 現在値
            loss_cut_rate: ロスカットレート
            loss_cut_width: ロスカット幅
            order_type: 取引方向（BUY/SELL）

        Returns:
            OrderEntry: 注文エントリー
        """
        # 必要証拠金（常に同じ）
        required_margin = order_price * quantity

        if order_type == ORDER_TYPE_BUY:
            # 買いポジションの場合
            # 任意証拠金 = (注文価格 - ロスカット幅 - ロスカットレート) * 数量 * レバレッジ
            optional_margin = max(0, (order_price - loss_cut_width - loss_cut_rate) * quantity * self.LEVERAGE)
            # 損益 = (現在値 - 注文価格) * 数量 * レバレッジ
            profit_loss = (current_price - order_price) * quantity * self.LEVERAGE
        else:
            # 売りポジションの場合
            # 任意証拠金 = (ロスカットレート + ロスカット幅 - 注文価格) * 数量 * レバレッジ
            optional_margin = max(0, (loss_cut_rate + loss_cut_width - order_price) * quantity * self.LEVERAGE)
            # 損益 = (注文価格 - 現在値) * 数量 * レバレッジ
            profit_loss = (order_price - current_price) * quantity * self.LEVERAGE

        return OrderEntry(
            price=order_price,
            amount=order_amount,
            quantity=quantity,
            required_margin=required_margin,
            optional_margin=optional_margin,
            profit_loss=profit_loss
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