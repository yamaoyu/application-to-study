# ADR 0001: 金額をDecimalで扱い、APIレスポンスを固定小数点文字列に統一する

- ステータス: 採用
- 決定日: 2026-11-14

## コンテキスト

給与、ボーナス、ペナルティなどの金額を`float`で扱うと、2進浮動小数点数に由来する丸め誤差が発生する可能性がある。

また、DBカラムを`DECIMAL(10, 2)`へ変更すると、SQLAlchemyは値をPythonの`Decimal`として返す。Pydanticは`Decimal`をJSON文字列に変換するが、入力や計算結果が持つ小数桁によって`"23.0"`、`"23.00"`、`"0.0"`など、レスポンスの表現が揺れる可能性がある。

金額の正確性を維持し、API利用者がレスポンス形式を予測できるようにする必要がある。

## 決定

### 金額の内部表現

給与、ボーナス、ペナルティ、およびそれらから計算される金額は、Pythonでは`Decimal`として扱う。

金額計算の途中で`float`へ変換しない。時間など、引き続き`float`で扱う値を金額計算に使用する場合は、計算の境界で`Decimal(str(value))`に変換する。

金額計算の丸めは、シリアライズ時ではなくドメインの計算処理で行う。丸め方式は既存の業務ルールに従う。

### DBでの保存形式

金額カラムは`DECIMAL(10, 2)`で定義する。SQLAlchemyの型注釈には`Mapped[Decimal]`を使用する。

対象には少なくとも次のカラムを含む。

- `incomes.salary`
- `activities.bonus`
- `activities.penalty`

既存カラムの型変更は、モデル定義の変更だけでなくAlembicマイグレーションでも行う。

### API入力

API入力は柔軟に受け付ける。例えば、次の入力はいずれも有効な金額として扱う。

```json
{"salary": 23}
```

```json
{"salary": 23.0}
```

```json
{"salary": 23.00}
```

```json
{"salary": "23.00"}
```

入力時の表記を固定小数点形式に強制しない。Pydanticで`Decimal`へ変換し、許容桁数などの入力制約を検証する。

数値として解釈できない入力に対するPydanticの`decimal_parsing`エラーは、既存のAPIエラー契約に従い`INVALID_NUMBER`へ変換する。

### APIレスポンス

金額は、小数第2位までを必ず含む固定小数点文字列として返す。

```json
{
  "base_income": "23.00",
  "pay_adjustment": "0.00",
  "total_bonus": "0.00",
  "total_penalty": "0.00"
}
```

JSONの数値ではなく文字列として返すことで、API利用側で浮動小数点数へ暗黙に変換されて精度が失われることを防ぐ。

### Pydanticでの共通化

レスポンス形式は個々のモデルに`field_serializer`を重複して定義せず、`Decimal`に検証とシリアライズ設定を付けた共通の型エイリアスで統一する。この型エイリアスはPydanticの`BaseModel`ではない。

実装例を以下に示す。

```python
from decimal import Decimal
from typing import Annotated

from pydantic import Field, PlainSerializer


def serialize_money(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


Money = Annotated[
    Decimal,
    Field(max_digits=10, decimal_places=2),
    PlainSerializer(
        serialize_money,
        return_type=str,
        when_used="json",
    ),
]
```

金額を扱うPydanticモデルでは、直接`Decimal`を指定する代わりにこの共通型を使用する。

```python
class RegisterSalaryResponse(BaseModel):
    year: int
    month: int
    salary: Money
```

### テスト

APIレスポンスのテストでは、`str(float_value)`から期待値を生成しない。API仕様である固定小数点文字列を明示する。

```python
assert response.json()["salary"] == "23.00"
```

入力の柔軟性と出力の一貫性は別々にテストする。

## 結果

### 利点

- 金額計算とDB保存で浮動小数点誤差を避けられる。
- 金額レスポンスの小数桁が常に一定になる。
- シリアライズ処理の重複を避けられる。
- 入力形式を過度に制限せず、API利用者の利便性を維持できる。
- テストがPythonの`float`の文字列表現に依存しなくなる。

### トレードオフ

- API利用側は金額をJSON文字列として扱う必要がある。
- 既存の`number`前提のフロントエンド型や計算処理は、文字列またはDecimal対応ライブラリを扱うように見直す必要がある。
- `Decimal`と`float`は直接演算できないため、時間から金額を計算する境界などで明示的な変換が必要になる。
- DBモデル、マイグレーション、ドメインモデル、APIモデル、テストを一貫して変更する必要がある。

## 検討した代替案

### 金額を引き続きfloatで扱う

実装変更は少ないが、金額計算に浮動小数点誤差が混入する可能性があるため採用しない。

### 金額を最小通貨単位の整数で扱う

浮動小数点誤差を避けられるが、このアプリケーションは万円単位の小数を扱っており、既存の入出力や計算処理への変更が大きくなるため今回は採用しない。

### 入力にも固定小数点文字列を強制する

形式は統一できるが、JSON数値による自然な入力まで拒否することになり、入力側の負担が増えるため採用しない。

### レスポンスをJSON数値として返す

フロントエンドで扱いやすい一方、JSONおよびJavaScriptの数値として扱われた時点でDecimalの精度保証が失われるため採用しない。
