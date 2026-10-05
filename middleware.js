// 株主専用ポータル（デモ）の入口。合言葉が合うまで、どのページも返さない。
// 合言葉は Vercel の環境変数に置く。このファイルには書かない。
//   PORTAL_PASSPHRASE … 株主用ページの合言葉
//   ADMIN_PASSPHRASE  … 管理画面の合言葉
export const config = { matcher: '/((?!_vercel).*)' };

const PUBLIC = new Set(['/login', '/login.html', '/admin-login', '/admin-login.html', '/assets/style.css', '/favicon.ico']);

async function tokenOf(kind, pass) {
  const data = new TextEncoder().encode(`ns-portal:${kind}:${pass}`);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function readCookie(request, name) {
  const raw = request.headers.get('cookie') || '';
  for (const part of raw.split(';')) {
    const [k, ...v] = part.trim().split('=');
    if (k === name) return v.join('=');
  }
  return '';
}

function redirect(url, to, cookies = []) {
  const headers = new Headers({ Location: new URL(to, url).toString(), 'Cache-Control': 'no-store' });
  for (const c of cookies) headers.append('Set-Cookie', c);
  return new Response(null, { status: 303, headers });
}

const cookieAttr = 'Path=/; HttpOnly; Secure; SameSite=Lax';

export default async function middleware(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  const portalPass = process.env.PORTAL_PASSPHRASE;
  const adminPass = process.env.ADMIN_PASSPHRASE;

  if (!portalPass) {
    return new Response('設定が未完了です。Vercel の環境変数 PORTAL_PASSPHRASE を設定してください。', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }

  if (path === '/logout') {
    return redirect(url, '/login', [`ns_auth=; Max-Age=0; ${cookieAttr}`, `ns_admin=; Max-Age=0; ${cookieAttr}`]);
  }

  if (path === '/auth' && request.method === 'POST') {
    const form = await request.formData();
    const kind = form.get('kind') === 'admin' ? 'admin' : 'portal';
    const input = String(form.get('passphrase') || '');
    if (kind === 'admin') {
      if (!adminPass || input !== adminPass) return redirect(url, '/admin-login?e=1');
      return redirect(url, '/admin', [`ns_admin=${await tokenOf('admin', adminPass)}; Max-Age=28800; ${cookieAttr}`]);
    }
    if (form.get('agree') !== 'yes') return redirect(url, '/login?e=2');
    if (input !== portalPass) return redirect(url, '/login?e=1');
    return redirect(url, '/', [`ns_auth=${await tokenOf('portal', portalPass)}; Max-Age=28800; ${cookieAttr}`]);
  }

  if (PUBLIC.has(path)) return;

  if (path === '/admin' || path.startsWith('/admin.') || path.startsWith('/admin/')) {
    if (adminPass && readCookie(request, 'ns_admin') === (await tokenOf('admin', adminPass))) return;
    return redirect(url, '/admin-login');
  }

  if (readCookie(request, 'ns_auth') === (await tokenOf('portal', portalPass))) return;
  return redirect(url, '/login');
}
