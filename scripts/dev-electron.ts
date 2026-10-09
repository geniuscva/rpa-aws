import { spawn } from 'node:child_process';
import { resolve } from 'node:path';
import { resolveElectronBinary } from '../src/main/electron-preflight.ts';

const preflight = resolveElectronBinary();
if (!preflight.ok) {
  console.error(preflight.message);
  process.exit(1);
}

const electronBin = resolve('node_modules/.bin/electron');
const child = spawn(electronBin, ['.'], { stdio: 'inherit', env: { ...process.env, NODE_ENV: 'development', AGENTICOS_DEV_SERVER: 'http://127.0.0.1:5173' } });
child.on('exit', (code) => process.exit(code ?? 0));
process.on('SIGINT', () => child.kill('SIGINT'));
process.on('SIGTERM', () => child.kill('SIGTERM'));
