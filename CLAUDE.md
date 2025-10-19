# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
日経225 CFD取引におけるリスク計算を行うPySide6ベースのGUIアプリケーション。
仕掛けレンジ内での発注計画と詳細なリスク分析（必要証拠金、任意証拠金、損益計算等）を提供します。

## Development Setup
- **Python**: 3.11以上（.python-versionで指定）
- **パッケージ管理**: uv
- **GUIフレームワーク**: PySide6 (>=6.9.1)
- **仮想環境**: .venvディレクトリに設定済み

## Commands
### Running the Application
```bash
python main.py
```

GUIアプリケーションが起動し、パラメータ入力、リスク分析サマリー、注文一覧表が表示されます。

### Testing
```bash
python test_order_types.py
```

### Syntax Check
```bash
python -m py_compile main.py
```

## Project Structure
```
n225-risk-calc/
├── main.py                 # エントリーポイント（GUIアプリ起動）
├── pyproject.toml          # プロジェクト設定と依存関係
├── Requirements.md         # 詳細な要件定義書
├── CLAUDE.md              # 本ファイル
├── README.md              # プロジェクト概要とドキュメント
├── test_order_types.py    # 注文タイプのテスト
└── src/
    ├── __init__.py
    ├── models.py          # データモデル（OrderRange, OrderEntry, RiskAnalysis）
    ├── calculator.py      # リスク計算エンジン（RiskCalculator）
    ├── validator.py       # 入力バリデーション（InputValidator）
    ├── formatter.py       # 結果フォーマッター（ResultFormatter）
    ├── constants.py       # 定数定義（デフォルト値、取引方向等）
    └── gui/
        ├── __init__.py
        └── main_window.py # メインウィンドウ（MainWindow）
```

## Architecture
### データフロー
1. **入力**: ユーザーがGUIからパラメータを入力
   - 仕掛けレンジ（開始価格、終了価格）
   - 値幅、取引数量
   - 現在値、ロスカットレート、ロスカット幅

2. **バリデーション**: InputValidatorで入力値を検証

3. **計算**: RiskCalculatorでリスク分析を実行
   - 注文生成（買い上がり/売り下がりの自動判定）
   - 必要証拠金・任意証拠金の計算
   - 損益計算

4. **出力**: ResultFormatterで結果を整形し、GUIに表示
   - リスク分析サマリー
   - 注文一覧テーブル

### 主要クラス
- **OrderRange**: 仕掛けレンジの設定を保持
- **OrderEntry**: 個別注文の情報を保持
- **RiskAnalysis**: リスク分析結果を保持
- **RiskCalculator**: リスク計算ロジックを実装
- **InputValidator**: 入力バリデーションロジックを実装
- **ResultFormatter**: 結果の整形処理を実装
- **MainWindow**: PySide6のメインウィンドウ

### 取引方向の自動判定
- 開始価格 < 終了価格 → 買い上がり（BUY）
- 開始価格 > 終了価格 → 売り下がり（SELL）

### 計算式
- **必要証拠金**: 注文価格 × 取引数量
- **任意証拠金（買い）**: max(0, (注文価格 - ロスカット幅 - ロスカットレート) × 数量 × レバレッジ)
- **任意証拠金（売り）**: max(0, (ロスカットレート - (注文価格 + ロスカット幅)) × 数量 × レバレッジ)
- **損益（買い）**: (現在値 - 注文価格) × 数量 × レバレッジ
- **損益（売り）**: (注文価格 - 現在値) × 数量 × レバレッジ
- **レバレッジ**: 10倍（定数）

## Important Notes
- デフォルトのロスカット幅は2139円（constants.pyで定義）
- デフォルトの取引数量は0.1（constants.pyで定義）
- 金額は3桁区切りカンマで表示
- 損益は正負の符号付きで表示

## Future Enhancements
詳細は[Requirements.md](Requirements.md)のPhase 2, 3を参照してください：
- CSV出力機能
- チャート表示
- レンジブレイク分析
- 資金効率計算