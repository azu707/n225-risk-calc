# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
日経225のリスク計算を行うPythonプロジェクト。現在は基本的なプロジェクト構造のみが設定されている初期段階です。

## Development Setup
- Python 3.11を使用（.python-versionで指定）
- uvを使用
- 仮想環境は.venvディレクトリに設定済み

## Commands
### Running the Application
```bash
python main.py
```

### Syntax Check
```bash
python -m py_compile main.py
```

## Project Structure
- `main.py`: エントリーポイント。現在は基本的なHello Worldメッセージを出力
- `pyproject.toml`: プロジェクトの依存関係とメタデータ設定
- `.python-version`: Python 3.11を指定
- `.gitignore`: Python標準的な除外ファイル設定（__pycache__、.venv等）

## Architecture
現在のプロジェクトは最小構成で、今後日経225のリスク計算機能が追加される予定です。拡張時は以下を考慮してください：
- データ取得モジュール
- リスク計算ロジック
- 結果出力・可視化機能