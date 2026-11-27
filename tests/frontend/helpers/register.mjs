// Lets `node --test` load the real frontend sources (TS, TSX, "@/..." and extensionless imports) without any new
// dependency: Node's module hooks plus the TypeScript compiler that the frontend already has installed.
// The packages that need a browser or a phone are swapped for the small fakes in ./fakes.
// Import this FIRST, then load app modules with `await import(...)`.
import { registerHooks, createRequire } from 'node:module';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
export const FRONTEND = path.resolve(here, '../../..'); // the app is at the repo root
const ROOT_URL = pathToFileURL(FRONTEND + path.sep).href;
const ts = createRequire(path.join(FRONTEND, 'package.json'))('typescript');

const fake = (name) => pathToFileURL(path.join(here, 'fakes', name)).href;
const FAKES = {
  react: fake('react.mjs'),
  'react/jsx-runtime': fake('react.mjs'),
  '@vis.gl/react-google-maps': fake('google-maps-react.mjs'),
  'next/dynamic': fake('next-dynamic.mjs'),
  '@capacitor/core': fake('capacitor-core.mjs'),
  '@capacitor-community/text-to-speech': fake('tts.mjs'),
};

const isFile = (p) => existsSync(p) && statSync(p).isFile();

function resolveSource(base) {
  for (const candidate of [base, `${base}.ts`, `${base}.tsx`, path.join(base, 'index.ts')]) {
    if (isFile(candidate)) return pathToFileURL(candidate).href;
  }
  return null;
}

registerHooks({
  resolve(specifier, context, nextResolve) {
    if (FAKES[specifier]) return { url: FAKES[specifier], shortCircuit: true };
    let base = null;
    if (specifier.startsWith('@/')) base = path.join(FRONTEND, specifier.slice(2));
    else if (specifier.startsWith('.') && context.parentURL?.startsWith('file:')) {
      base = path.resolve(path.dirname(fileURLToPath(context.parentURL)), specifier);
    }
    if (base) {
      const url = resolveSource(base);
      if (url) return { url, shortCircuit: true };
    }
    return nextResolve(specifier, context);
  },
  load(url, context, nextLoad) {
    const own = url.startsWith(ROOT_URL) && !/\/(node_modules|tests)\//.test(url.slice(ROOT_URL.length - 1));
    if (own && /\.tsx?$/.test(url)) {
      const source = readFileSync(fileURLToPath(url), 'utf8');
      const out = ts.transpileModule(source, {
        fileName: fileURLToPath(url),
        compilerOptions: {
          module: ts.ModuleKind.ESNext,
          target: ts.ScriptTarget.ES2022,
          jsx: ts.JsxEmit.ReactJSX,
          esModuleInterop: true,
          isolatedModules: true,
        },
      });
      return { format: 'module', source: out.outputText, shortCircuit: true };
    }
    return nextLoad(url, context);
  },
});
