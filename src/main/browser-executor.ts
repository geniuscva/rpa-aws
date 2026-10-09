import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';
import { join } from 'node:path';
import { chromium, type BrowserContext, type Page } from 'playwright';

function isPrivateIp(address: string): boolean {
  const normalized = address.toLowerCase();
  if (normalized === '::' || normalized === '::1' || normalized.startsWith('fe80:') || /^f[cd][0-9a-f]*:/i.test(normalized) || normalized.startsWith('ff')) return true;
  const mapped = normalized.match(/^::ffff:([0-9a-f]{1,4}):([0-9a-f]{1,4})$/);
  if (mapped) {
    const high = Number.parseInt(mapped[1]!, 16);
    const low = Number.parseInt(mapped[2]!, 16);
    return isPrivateIp(`${high >> 8}.${high & 255}.${low >> 8}.${low & 255}`);
  }
  if (normalized.startsWith('::ffff:')) return isPrivateIp(normalized.slice(7));
  if (!isIP(address)) return false;
  if (isIP(address) === 6) return !/^[23][0-9a-f]{0,3}:/i.test(normalized);
  const octets = address.split('.').map(Number);
  const [a, b] = octets;
  return a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) || (a === 172 && b! >= 16 && b <= 31) || (a === 192 && b === 168) || a! >= 224;
}

export async function assertPublicUrl(raw: string): Promise<URL> {
  let url: URL;
  try { url = new URL(raw); } catch { throw new Error('Enter a valid web address.'); }
  if (!['https:', 'http:'].includes(url.protocol) || !url.hostname || url.username || url.password) throw new Error('Only public HTTP or HTTPS pages are allowed.');
  const host = url.hostname.toLowerCase().replace(/^\[|\]$/g, '');
  if (host === 'localhost' || host.endsWith('.localhost') || host.endsWith('.local') || host.endsWith('.internal')) throw new Error('Private network addresses are blocked.');
  if (isIP(host)) {
    if (isPrivateIp(host)) throw new Error('Private network addresses are blocked.');
  } else {
    let records;
    try { records = await lookup(host, { all: true, verbatim: true }); }
    catch { throw new Error('This host could not be verified as a public network address.'); }
    if (!records.length || records.some((record) => isPrivateIp(record.address))) throw new Error('This host resolves to a private network address.');
  }
  url.hash = '';
  return url;
}

export class BrowserExecutor {
  private context?: BrowserContext;
  private page?: Page;
  private starting?: Promise<BrowserContext>;

  constructor(private readonly userDataPath: string) {}

  async open(rawUrl: string): Promise<{ url: string; title: string }> {
    const url = await assertPublicUrl(rawUrl);
    const page = await this.getPage();
    await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 30_000 });
    return { url: page.url(), title: await page.title() };
  }

  async snapshot(): Promise<{ url: string; title: string; text: string; links: Array<{ index: number; text: string; url: string }> }> {
    const page = await this.getPage();
    const text = await page.locator('body').innerText({ timeout: 8_000 }).catch(() => '');
    const links = await page.locator('a[href]').evaluateAll((nodes) => nodes.slice(0, 100).map((node) => {
      const anchor = node as HTMLAnchorElement;
      return { text: (anchor.innerText || anchor.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 160), url: anchor.href };
    }));
    const safeLinks: Array<{ index: number; text: string; url: string }> = [];
    for (const [index, link] of links.entries()) {
      try { safeLinks.push({ index, text: link.text || '(untitled link)', url: (await assertPublicUrl(link.url)).toString() }); } catch { /* hide unsafe links */ }
    }
    return { url: page.url(), title: await page.title(), text: text.slice(0, 24_000), links: safeLinks };
  }

  async clickLink(index: number): Promise<{ url: string; title: string }> {
    if (!Number.isInteger(index) || index < 0 || index > 99) throw new Error('Choose a link index from the latest page snapshot.');
    const page = await this.getPage();
    const links = await page.locator('a[href]').all();
    const link = links[index];
    if (!link) throw new Error('Link was not found. Refresh the page snapshot and try again.');
    const href = await link.getAttribute('href');
    const absolute = new URL(href ?? '', page.url()).toString();
    await assertPublicUrl(absolute);
    await link.click({ timeout: 10_000 });
    await page.waitForLoadState('domcontentloaded', { timeout: 8_000 }).catch(() => undefined);
    await assertPublicUrl(page.url());
    return { url: page.url(), title: await page.title() };
  }

  async close(): Promise<void> { await this.context?.close(); this.context = undefined; this.page = undefined; }

  private async getPage(): Promise<Page> {
    if (this.page && !this.page.isClosed()) return this.page;
    const context = await (this.starting ??= this.launch());
    this.starting = undefined;
    this.page = context.pages()[0] ?? await context.newPage();
    return this.page;
  }

  private async launch(): Promise<BrowserContext> {
    const context = await chromium.launchPersistentContext(join(this.userDataPath, 'browser-profile'), {
      headless: false,
      viewport: { width: 1440, height: 960 },
      args: ['--disable-background-networking', '--disable-component-update', '--disable-sync'],
    });
    await context.route('**/*', async (route) => {
      try { await assertPublicUrl(route.request().url()); await route.continue(); }
      catch { await route.abort('blockedbyclient'); }
    });
    this.context = context;
    return context;
  }
}
