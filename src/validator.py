from typing import Optional, Tuple

from .constants import DEFAULT_LOSS_CUT_WIDTH, DEFAULT_QUANTITY


class InputValidator:
    """入力値のバリデーションを行うクラス"""
    
    # 日経225の合理的な価格範囲（参考値）
    MIN_PRICE = 10000      # 最小価格（円）
    MAX_PRICE = 100000     # 最大価格（円）
    MIN_ORDER_AMOUNT = 100  # 最小注文金額（円）
    MAX_ORDER_AMOUNT = 50000  # 最大注文金額（円）
    MIN_QUANTITY = 0.1     # 最小取引数量
    MAX_QUANTITY = 100.0   # 最大取引数量
    
    @staticmethod
    def validate_price_range(start_price: int, end_price: int) -> Tuple[bool, Optional[str]]:
        """
        価格レンジのバリデーション

        Args:
            start_price: 開始価格
            end_price: 終了価格

        Returns:
            Tuple[bool, Optional[str]]: (有効性, エラーメッセージ)
        """
        # 価格の範囲チェック
        if start_price < InputValidator.MIN_PRICE:
            return False, f"開始価格は{InputValidator.MIN_PRICE:,}円以上である必要があります"

        if start_price > InputValidator.MAX_PRICE:
            return False, f"開始価格は{InputValidator.MAX_PRICE:,}円以下である必要があります"

        if end_price < InputValidator.MIN_PRICE:
            return False, f"終了価格は{InputValidator.MIN_PRICE:,}円以上である必要があります"

        if end_price > InputValidator.MAX_PRICE:
            return False, f"終了価格は{InputValidator.MAX_PRICE:,}円以下である必要があります"

        # 開始価格と終了価格が同じ場合はエラー
        if start_price == end_price:
            return False, "開始価格と終了価格は異なる値である必要があります"

        # 価格差の妥当性チェック（買い上がり・売り下がり両方に対応）
        price_diff = abs(end_price - start_price)
        if price_diff < 100:
            return False, "価格レンジは最低100円以上である必要があります"

        if price_diff > 20000:
            return False, "価格レンジは20,000円以下にしてください"

        return True, None
    
    @staticmethod
    def validate_order_amount(order_amount: int) -> Tuple[bool, Optional[str]]:
        """
        値幅のバリデーション
        
        Args:
            order_amount: 値幅
            
        Returns:
            Tuple[bool, Optional[str]]: (有効性, エラーメッセージ)
        """
        if order_amount < InputValidator.MIN_ORDER_AMOUNT:
            return False, f"値幅は{InputValidator.MIN_ORDER_AMOUNT:,}円以上である必要があります"
        
        if order_amount > InputValidator.MAX_ORDER_AMOUNT:
            return False, f"値幅は{InputValidator.MAX_ORDER_AMOUNT:,}円以下である必要があります"
        
        return True, None
    
    @staticmethod
    def validate_quantity(quantity: float) -> Tuple[bool, Optional[str]]:
        """
        取引数量のバリデーション
        
        Args:
            quantity: 取引数量
            
        Returns:
            Tuple[bool, Optional[str]]: (有効性, エラーメッセージ)
        """
        if quantity < InputValidator.MIN_QUANTITY:
            return False, f"取引数量は{InputValidator.MIN_QUANTITY}以上である必要があります"
        
        if quantity > InputValidator.MAX_QUANTITY:
            return False, f"取引数量は{InputValidator.MAX_QUANTITY}以下である必要があります"
        
        # 小数点第1位までの値かチェック
        if round(quantity * 10) != quantity * 10:
            return False, "取引数量は小数点第1位までの値で入力してください"
        
        return True, None
    
    @staticmethod
    def validate_all_inputs(start_price: int, end_price: int, order_amount: int, quantity: float = DEFAULT_QUANTITY, current_price: int = 0, loss_cut_rate: int = 0, loss_cut_width: int = DEFAULT_LOSS_CUT_WIDTH) -> Tuple[bool, Optional[str]]:
        """
        全ての入力値を一括でバリデーション
        
        Args:
            start_price: 開始価格
            end_price: 終了価格
            order_amount: 値幅
            quantity: 取引数量
            current_price: 現在値
            loss_cut_rate: ロスカットレート
            loss_cut_width: ロスカット幅
            
        Returns:
            Tuple[bool, Optional[str]]: (有効性, エラーメッセージ)
        """
        # 価格レンジのバリデーション
        is_valid, error_msg = InputValidator.validate_price_range(start_price, end_price)
        if not is_valid:
            return is_valid, error_msg
        
        # 注文金額のバリデーション
        is_valid, error_msg = InputValidator.validate_order_amount(order_amount)
        if not is_valid:
            return is_valid, error_msg
        
        # 取引数量のバリデーション
        is_valid, error_msg = InputValidator.validate_quantity(quantity)
        if not is_valid:
            return is_valid, error_msg
        
        # 現在値のバリデーション
        if current_price <= 0:
            return False, "現在値は正の値である必要があります"
        
        if current_price < InputValidator.MIN_PRICE or current_price > InputValidator.MAX_PRICE:
            return False, f"現在値は{InputValidator.MIN_PRICE:,}円〜{InputValidator.MAX_PRICE:,}円の範囲で入力してください"
        
        # ロスカットレートのバリデーション
        if loss_cut_rate <= 0:
            return False, "ロスカットレートは正の値である必要があります"
        
        if loss_cut_rate < InputValidator.MIN_PRICE or loss_cut_rate > InputValidator.MAX_PRICE:
            return False, f"ロスカットレートは{InputValidator.MIN_PRICE:,}円〜{InputValidator.MAX_PRICE:,}円の範囲で入力してください"
        
        # ロスカット幅のバリデーション
        if loss_cut_width <= 0:
            return False, "ロスカット幅は正の値である必要があります"
        
        if loss_cut_width > 10000:
            return False, "ロスカット幅は10,000円以下である必要があります"
        
        # 追加のロジックチェック
        price_range = abs(end_price - start_price)
        if order_amount > price_range:
            return False, "値幅が価格レンジより大きい場合、1つの注文のみが生成されます"

        # 注文数の妥当性チェック
        estimated_orders = (price_range + order_amount - 1) // order_amount
        if estimated_orders > 1000:
            return False, "注文数が多すぎます。値幅を大きくするか、価格レンジを小さくしてください"

        return True, None
    
    @staticmethod
    def parse_quantity_input(quantity_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        取引数量入力文字列をパースして浮動小数点数に変換
        
        Args:
            quantity_str: 取引数量の文字列
            
        Returns:
            Tuple[bool, Optional[float], Optional[str]]: (成功, 数量値, エラーメッセージ)
        """
        try:
            quantity_value = float(quantity_str.strip())
            return True, quantity_value, None
        except ValueError:
            return False, None, "有効な数値を入力してください"
    
    @staticmethod
    def parse_price_input(price_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        価格入力文字列をパースして整数に変換
        
        Args:
            price_str: 価格の文字列（カンマ区切り対応）
            
        Returns:
            Tuple[bool, Optional[int], Optional[str]]: (成功, 価格値, エラーメッセージ)
        """
        try:
            # カンマを除去してから整数に変換
            cleaned_str = price_str.replace(',', '').replace('円', '').strip()
            price_value = int(cleaned_str)
            return True, price_value, None
        except ValueError:
            return False, None, "有効な数値を入力してください"