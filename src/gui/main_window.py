import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QTextEdit, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..models import OrderRange
from ..calculator import RiskCalculator
from ..validator import InputValidator
from ..formatter import ResultFormatter


class MainWindow(QMainWindow):
    """日経225 CFD リスク計算アプリのメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.calculator = RiskCalculator()
        self.validator = InputValidator()
        self.formatter = ResultFormatter()
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("日経225 CFD リスク計算アプリ")
        self.setGeometry(100, 100, 1000, 700)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # スプリッター（上下分割）
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 入力部分
        input_widget = self.create_input_section()
        splitter.addWidget(input_widget)
        
        # 結果表示部分
        result_widget = self.create_result_section()
        splitter.addWidget(result_widget)
        
        # スプリッターの初期サイズ設定
        splitter.setSizes([250, 450])
        
    def create_input_section(self) -> QWidget:
        """入力セクションの作成"""
        group_box = QGroupBox("パラメータ設定")
        layout = QGridLayout(group_box)
        
        # フォント設定
        font = QFont()
        font.setPointSize(10)
        
        # 開始価格入力
        layout.addWidget(QLabel("開始価格（円）:"), 0, 0)
        self.start_price_edit = QLineEdit()
        self.start_price_edit.setPlaceholderText("例: 40000")
        self.start_price_edit.setFont(font)
        layout.addWidget(self.start_price_edit, 0, 1)
        
        # 終了価格入力
        layout.addWidget(QLabel("終了価格（円）:"), 1, 0)
        self.end_price_edit = QLineEdit()
        self.end_price_edit.setPlaceholderText("例: 41000")
        self.end_price_edit.setFont(font)
        layout.addWidget(self.end_price_edit, 1, 1)
        
        # 値幅入力
        layout.addWidget(QLabel("値幅（円）:"), 2, 0)
        self.order_amount_edit = QLineEdit()
        self.order_amount_edit.setPlaceholderText("例: 100")
        self.order_amount_edit.setFont(font)
        layout.addWidget(self.order_amount_edit, 2, 1)
        
        # 計算ボタン
        self.calculate_button = QPushButton("計算実行")
        self.calculate_button.setFont(font)
        self.calculate_button.clicked.connect(self.calculate_risk)
        layout.addWidget(self.calculate_button, 3, 0, 1, 2)
        
        # クリアボタン
        self.clear_button = QPushButton("クリア")
        self.clear_button.setFont(font)
        self.clear_button.clicked.connect(self.clear_inputs)
        layout.addWidget(self.clear_button, 4, 0, 1, 2)
        
        return group_box
    
    def create_result_section(self) -> QWidget:
        """結果表示セクションの作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # サマリー表示
        summary_group = QGroupBox("リスク分析サマリー")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        # 注文一覧テーブル
        table_group = QGroupBox("注文一覧")
        table_layout = QVBoxLayout(table_group)
        
        self.order_table = QTableWidget()
        self.setup_table()
        table_layout.addWidget(self.order_table)
        
        layout.addWidget(table_group)
        
        return widget
    
    def setup_table(self):
        """テーブルの設定"""
        headers = self.formatter.format_table_headers()
        self.order_table.setColumnCount(len(headers))
        self.order_table.setHorizontalHeaderLabels(headers)
        
        # テーブルの列幅を調整
        self.order_table.setColumnWidth(0, 80)   # 注文番号
        self.order_table.setColumnWidth(1, 120)  # 注文価格
        self.order_table.setColumnWidth(2, 120)  # 発注金額
        self.order_table.setColumnWidth(3, 120)  # 必要証拠金
        
    def calculate_risk(self):
        """リスク計算の実行"""
        try:
            # 入力値の取得と解析
            start_price_text = self.start_price_edit.text().strip()
            end_price_text = self.end_price_edit.text().strip()
            order_amount_text = self.order_amount_edit.text().strip()
            
            if not all([start_price_text, end_price_text, order_amount_text]):
                self.show_error("全ての項目を入力してください。")
                return
            
            # 文字列を数値に変換
            success, start_price, error = self.validator.parse_price_input(start_price_text)
            if not success:
                self.show_error(f"開始価格の入力エラー: {error}")
                return
            
            success, end_price, error = self.validator.parse_price_input(end_price_text)
            if not success:
                self.show_error(f"終了価格の入力エラー: {error}")
                return
            
            success, order_amount, error = self.validator.parse_price_input(order_amount_text)
            if not success:
                self.show_error(f"値幅の入力エラー: {error}")
                return
            
            # 入力値のバリデーション
            is_valid, error_msg = self.validator.validate_all_inputs(
                start_price, end_price, order_amount
            )
            if not is_valid:
                self.show_error(error_msg)
                return
            
            # リスク計算の実行
            order_range = OrderRange(
                start_price=start_price,
                end_price=end_price,
                order_amount=order_amount
            )
            
            analysis = self.calculator.calculate_orders(order_range)
            
            # 結果の表示
            self.display_results(analysis)
            
        except Exception as e:
            self.show_error(f"計算エラーが発生しました: {str(e)}")
    
    def display_results(self, analysis):
        """計算結果の表示"""
        # サマリーの表示
        summary_text = self.formatter.format_summary(analysis)
        self.summary_text.setPlainText(summary_text)
        
        # テーブルの更新
        self.update_table(analysis.order_list)
    
    def update_table(self, order_list):
        """テーブルの更新"""
        self.order_table.setRowCount(len(order_list))
        
        for i, entry in enumerate(order_list):
            row_data = self.formatter.format_table_row(entry, i + 1)
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                # 数値列は右揃え
                if j > 0:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.order_table.setItem(i, j, item)
    
    def clear_inputs(self):
        """入力フィールドのクリア"""
        self.start_price_edit.clear()
        self.end_price_edit.clear()
        self.order_amount_edit.clear()
        self.summary_text.clear()
        self.order_table.setRowCount(0)
    
    def show_error(self, message: str):
        """エラーメッセージの表示"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("入力エラー")
        msg_box.setText(message)
        msg_box.exec()