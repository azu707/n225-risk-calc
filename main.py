import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    """日経225 CFD リスク計算アプリのメイン関数"""
    app = QApplication(sys.argv)
    
    # メインウィンドウの作成と表示
    window = MainWindow()
    window.show()
    
    # アプリケーションの実行
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
