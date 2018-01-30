# google_input

| master | [![Build Status](https://travis-ci.org/tomoemon/google_input.svg?branch=master)](https://travis-ci.org/tomoemon/google_input) |
| --- | --- |
| develop | [![Build Status](https://travis-ci.org/tomoemon/google_input.svg?branch=develop)](https://travis-ci.org/tomoemon/google_input) |

これは、Google 日本語入力のローマ字入力のアルゴリズムを実装してみたものです。

※Google 日本語入力のオープンソース版である mozc(https://github.com/google/mozc) のソースコードを直接参考にしたわけではなく、通常使用する際に観測できた挙動に従って実装してみたものであるため、実際の仕様とは異なる可能性があります。

## 実装動機

これまで何度かローマ字入力のアルゴリズムを実装する機会がありましたがとてもスマートとはいえない実装しかできませんでした。また、他のタイピングソフト作者らのローマ字入力アルゴリズムの実装をいくつか読む機会がありましたが、やはりいずれもローマ字入力特有の例外処理に苦労している様子が見られました。

一方で、Google 日本語入力のローマ字入力アルゴリズムが非常に簡潔でかつ柔軟性に富んでいるため、世の中のタイピングゲーム作者やキーボード入力のエミュレートソフトを作成している方々の参考になれば幸いと思い、試しに実装して公開することにしました。

## Google 日本語入力のローマ字入力アルゴリズムが素晴らしい理由

* 設定ファイルが簡潔である
  * 1行でルールが完結するシンプルな tsv
  * 人が読み書きしやすい
  * （少なくともローマ字入力を実現する上で）書くべき内容が必要最低限
* アルゴリズムが簡潔
  * 設定ファイルの読み書きを除くと、たかだか 30行 程度で実装可能
  * ローマ字入力における「っ」や「ん」で必要になるような例外処理に関する記述が一切不要
* 様々な配列を実現できる
  * 親指シフト等の同時押しが発生しない、逐次打鍵系の配列であれば基本的に実現可能（Shiftキーの同時押しについては問題ない）
  * 同じキーを連打するケータイ入力のような配列も実現可能

## アルゴリズムの概要

（あとで記載）

Google 日本語入力そのもののローマ字テーブルをカスタマイズする方法を把握していると話が早いです。
「次の入力」の概念については、下記ブログを参考にしてみてください。
http://tomoemon.hateblo.jp/entry/20101024/p1

また、入力文字列を与えた際に、ローマ字テーブルに最短一致したものをすぐに確定させるわけではなく、できるだけ評価を遅延させていることにも注意。共通のプレフィックス（n：ん、na：な　等）を持つルールに対応する入力を与えた際の挙動をイメージするとわかりやすいです。

# 開発環境

## Prerequisite

環境構築のために pipenv を使います

    pip install pipenv

## Setup

下記コマンドで開発に必要な python 環境を構築します。

    cd google_input
    pipenv install -d

Visual Studio Code をお使いの方は下記コマンドを実行すると、ワークスペース設定に適切な pythonPath を設定します。

    pipenv run python setup.py vscode

## Run Unittests

    pipenv run python -m pytest
