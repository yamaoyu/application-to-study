## 1. テストコード作成
```sh
npx playwright codegen --ignore-https-errors {URL}
```
--ignore-https-errorsはhttpsの証明書が自己署名の場合、Playwrightが安全でない証明書をデフォルトで弾くため  
こうならないならなくしても良い

## 2. テストコード実行手順
frontendディレクトリで以下のいずれかを実行
``` sh
npx playwright test (ファイル名)
npx playwright test --ui
npx playwright test --debug
```