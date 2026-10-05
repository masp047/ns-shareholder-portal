// 全ページ共通のヘッダーとフッターを差し込む。ナビを変えるときはこのファイルだけ直す。
const NAV = [
  ['/', 'ホーム'],
  ['/report', '月次レポート'],
  ['/library', '資料室'],
  ['/company', '会社概要'],
];
const here = location.pathname.replace(/\.html$/, '').replace(/\/index$/, '/') || '/';
const head = document.getElementById('site-head');
if (head) {
  head.className = 'site-head';
  head.innerHTML =
    '<div class="in"><a class="brand" href="/">日本信達 株主専用ポータル<small>SHAREHOLDER PORTAL</small></a><nav class="nav" aria-label="主ナビ">' +
    NAV.map(([p, t]) => `<a href="${p}"${p === here ? ' aria-current="page"' : ''}>${t}</a>`).join('') +
    '<a class="out" href="/logout">ログアウト</a></nav></div>';
}
const foot = document.getElementById('site-foot');
if (foot) {
  foot.className = 'site-foot';
  foot.innerHTML =
    '<div class="in">本ポータルの内容は株主限りです。転送・転載を禁じます。｜<a href="/disclaimer">将来予測に関する注意事項</a><br>日本信達株式会社</div>';
}
