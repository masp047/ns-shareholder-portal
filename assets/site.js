// 全ページ共通のヘッダーとフッターを差し込む。ナビを変えるときはこのファイルだけ直す。
const NAV = [
  ['/', 'ホーム'],
  ['/report', '月次レポート'],
  ['/library', '資料室'],
  ['/company', '会社概要'],
];
// 次期以降に作るページ。名前だけ出し、リンクは張らない。
const SOON = ['Q&A', '株主手続き'];
const here = location.pathname.replace(/\.html$/, '').replace(/\/index$/, '/') || '/';
const head = document.getElementById('site-head');
if (head) {
  head.className = 'site-head';
  head.innerHTML =
    '<div class="in"><a class="brand" href="/"><img class="logo" src="/assets/logo/shintatsu-white.png" width="267" height="38" alt="日本信達株式会社 SHINTATSU"></a><nav class="nav" aria-label="主ナビ">' +
    NAV.map(([p, t]) => `<a href="${p}"${p === here ? ' aria-current="page"' : ''}>${t}</a>`).join('') +
    SOON.map((t) => `<span class="soon">${t}</span>`).join('') +
    '<a class="out" href="/logout">ログアウト</a></nav></div>';
}
const foot = document.getElementById('site-foot');
if (foot) {
  foot.className = 'site-foot';
  foot.innerHTML =
    '<div class="in">本ポータルの内容は株主限りです。転送・転載を禁じます。｜<a href="/disclaimer">免責事項はこちら</a><br>日本信達株式会社</div>';
}
