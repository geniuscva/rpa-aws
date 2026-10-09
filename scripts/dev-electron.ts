import { spawn } from 'node:child_process';
import { resolve } from 'node:path';

const electronBin = resolve('node_modules/.bin/electron');
const child = spawn(electronBin, ['.'], { stdio: 'inherit', env: { ...process.env, NODE_ENV: 'development', AGENTICOS_DEV_SERVER: 'http://127.0.0.1:5173' } });
child.on('exit', (code) => process.exit(code ?? 0));
process.on('SIGINT', () => child.kill('SIGINT'));
process.on('SIGTERM', () => child.kill('SIGTERM'));
