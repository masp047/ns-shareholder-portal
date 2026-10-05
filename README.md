# NS株主ポータル（デモ）

日本信達株式会社の株主専用ポータルのデモサイトである。
サイトマップ v00.04（V1.0 立上げ版）に沿って作成した。

## 取り扱いの注意

- リポジトリは非公開のまま運用する。月次レポートの原稿を含む。
- 合言葉はリポジトリに書かない。Vercel の環境変数に置く。
- 公開URLと合言葉は、確認を依頼する相手にだけ伝える。

## 構成

| ファイル | 役割 |
| :--- | :--- |
| `middleware.js` | 入口。合言葉が合うまで、どのページも画像も返さない |
| `vercel.json` | URLの整形、検索エンジン除外、キャッシュ禁止 |
| `login.html` | ログイン画面（合言葉と利用条件への同意） |
| `index.html` | ホーム（社長ビデオレター、お知らせ一覧） |
| `report.html` | 月次レポート（常に当月号） |
| `library.html` | 資料室 |
| `company.html` | 会社概要 |
| `disclaimer.html` | 将来予測に関する注意事項 |
| `admin-login.html` / `admin.html` | 管理画面（画面の形のみ） |
| `assets/style.css` | 全ページ共通の見た目 |
| `assets/site.js` | 全ページ共通のヘッダーとフッター |
| `assets/img/` | 月次レポートの図版と写真 |
| `assets/docs/` | 資料室のPDF置き場 |

## Vercel への公開手順（初回のみ）

1. Vercel にログインし、「Add New → Project」でこのリポジトリを取り込む。
2. Framework Preset は「Other」を選ぶ。ビルド設定は空のままでよい。
3. 「Environment Variables」に次の2つを登録する。
   - `PORTAL_PASSPHRASE`：株主用ページの合言葉
   - `ADMIN_PASSPHRASE`：管理画面の合言葉
4. 「Deploy」を押す。
5. 公開後、合言葉を入れずに `/report` を開き、ログイン画面へ戻されることを確かめる。

以降は、GitHub の `main` を更新するたびに自動で再公開される。
環境変数を変えたときは、Vercel で再デプロイする。

## 月次の更新手順

1. `report.html` を `assets/archive/YYYY-MM.html` などへ複製し、`library.html` の「過去の月次レポート」に行を足す。
2. `report.html` を当月号の内容に書き換える。図版は `assets/img/` に置く。
3. `index.html` の「お知らせ一覧」に1行足す。
4. `main` に反映する。

## このデモで動かないもの

- 株主別のログイン履歴の記録（合言葉が全員共通のため、誰が入ったかは分からない）
- 管理画面の入力内容の保存
- 株主への通知メール

ログイン方式は別途検討中である。決まり次第 `middleware.js` を差し替える。
