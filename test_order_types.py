#!/usr/bin/env python3
"""
買い上がりと売り下がりのテストスクリプト
"""
from src.models import OrderRange
from src.calculator import RiskCalculator
from src.formatter import ResultFormatter
from src.constants import ORDER_TYPE_BUY, ORDER_TYPE_SELL

def test_buy_pattern():
    """買い上がりパターンのテスト"""
    print("=== 買い上がりパターンのテスト ===")
    calculator = RiskCalculator()
    formatter = ResultFormatter()

    order_range = OrderRange(
        start_price=10000,
        end_price=10500,
        order_amount=100,
        quantity=0.1,
        current_price=9500,
        loss_cut_rate=9000,
        loss_cut_width=2139
    )

    analysis = calculator.calculate_orders(order_range)
    print(formatter.format_summary(analysis))
    print(f"\n注文数: {len(analysis.order_list)}")
    print(f"最初の注文価格: {analysis.order_list[0].price}")
    print(f"最後の注文価格: {analysis.order_list[-1].price}")
    print(f"取引方向: {analysis.order_type}")
    assert analysis.order_type == ORDER_TYPE_BUY, "取引方向が買いであるべき"
    print("✅ 買い上がりパターンOK\n")

def test_sell_pattern():
    """売り下がりパターンのテスト"""
    print("=== 売り下がりパターンのテスト ===")
    calculator = RiskCalculator()
    formatter = ResultFormatter()

    order_range = OrderRange(
        start_price=10000,
        end_price=9500,
        order_amount=100,
        quantity=0.1,
        current_price=10500,
        loss_cut_rate=11000,
        loss_cut_width=2139
    )

    analysis = calculator.calculate_orders(order_range)
    print(formatter.format_summary(analysis))
    print(f"\n注文数: {len(analysis.order_list)}")
    print(f"最初の注文価格: {analysis.order_list[0].price}")
    print(f"最後の注文価格: {analysis.order_list[-1].price}")
    print(f"取引方向: {analysis.order_type}")
    assert analysis.order_type == ORDER_TYPE_SELL, "取引方向が売りであるべき"
    print("✅ 売り下がりパターンOK\n")

def test_profit_loss():
    """損益計算のテスト"""
    print("=== 損益計算のテスト ===")
    calculator = RiskCalculator()

    # 買いポジション: 現在値が注文価格より高い場合、利益
    buy_range = OrderRange(
        start_price=10000,
        end_price=10100,
        order_amount=100,
        quantity=0.1,
        current_price=10500,  # 注文価格より高い
        loss_cut_rate=9000,
        loss_cut_width=2139
    )
    buy_analysis = calculator.calculate_orders(buy_range)
    print(f"買いポジションの損益（現在値が上）: {buy_analysis.total_profit_loss}")
    assert buy_analysis.total_profit_loss > 0, "買いポジションで現在値が上なら利益"

    # 売りポジション: 現在値が注文価格より低い場合、利益
    sell_range = OrderRange(
        start_price=10000,
        end_price=9900,
        order_amount=100,
        quantity=0.1,
        current_price=9500,  # 注文価格より低い
        loss_cut_rate=11000,
        loss_cut_width=2139
    )
    sell_analysis = calculator.calculate_orders(sell_range)
    print(f"売りポジションの損益（現在値が下）: {sell_analysis.total_profit_loss}")
    assert sell_analysis.total_profit_loss > 0, "売りポジションで現在値が下なら利益"
    print("✅ 損益計算OK\n")

if __name__ == "__main__":
    test_buy_pattern()
    test_sell_pattern()
    test_profit_loss()
    print("🎉 すべてのテストが成功しました！")
