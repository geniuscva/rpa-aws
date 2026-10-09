import { describe, expect, it } from 'vitest';
import { assertPublicUrl } from './browser-executor.js';

describe('browser URL boundary', () => {
  it('accepts public HTTP and HTTPS URLs and removes fragments', async () => {
    expect((await assertPublicUrl('https://93.184.216.34/article#section')).hash).toBe('');
    expect((await assertPublicUrl('http://93.184.216.34')).protocol).toBe('http:');
  });

  it('rejects local hosts, private IPv4 and IPv4-mapped IPv6 addresses', async () => {
    await expect(assertPublicUrl('http://localhost')).rejects.toThrow('Private network');
    await expect(assertPublicUrl('http://192.168.1.1')).rejects.toThrow('Private network');
    await expect(assertPublicUrl('http://[::ffff:7f00:1]')).rejects.toThrow('Private network');
    await expect(assertPublicUrl('file:///etc/passwd')).rejects.toThrow('Only public HTTP');
  });
});
