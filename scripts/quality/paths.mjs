import fs from 'node:fs/promises';
import path from 'node:path';

export const areas = ['tools', 'docs', 'frontend', 'backend'];
export const preserved = ['harness-design', '.harness-state'];
const omitted = new Set([
  'artifacts',
  'evidence',
  'attachments',
  'raw',
  'originals',
  'node_modules',
  'build',
  'dist',
  '.gradle',
  '.git',
  '.tmp',
  '__pycache__',
]);
const rootFiles = [
  'AGENTS.md',
  'README.md',
  'STRUCTURE.md',
  'package.json',
  '.prettierrc.json',
  'compose.yaml',
];
export const roots = [
  ...rootFiles,
  '.github/workflows',
  '.codex/hooks.json',
  '.vscode',
  'docs',
  'harness',
  'work',
  'scripts',
  'frontend',
  'backend/src',
];
export const pathspecs = [
  '.',
  ':(top,exclude)harness-design',
  ':(top,exclude).harness-state',
];

export const pathKey = (name) =>
  process.platform === 'win32' ? name.toLowerCase() : name;

export function normalize(input) {
  if (typeof input !== 'string' || !input || /[\x00-\x1f*?\[\]]/.test(input))
    throw Error('Invalid file path; review the target.');
  const value = input.replaceAll('\\', '/');
  const parts = value.split('/');
  if (
    value.startsWith('/') ||
    parts.some(
      (p) =>
        !p || p === '..' || p === '.' || p.includes(':') || /[ .]$/.test(p),
    )
  )
    throw Error('File path escapes or is ambiguous; review the target.');
  return parts.join('/');
}

function excluded(name) {
  const parts = name.toLowerCase().split('/');
  return (
    preserved.includes(parts[0]) ||
    parts.some((p) => omitted.has(p)) ||
    parts.some((p) => p.startsWith('.env'))
  );
}

export function formatKind(input) {
  const name = normalize(input);
  if (
    [
      '.gitignore',
      '.gitattributes',
      '.prettierignore',
      'scripts/hooks/pre-commit',
    ].includes(name) ||
    name.endsWith('.gradle')
  )
    return 'skip';
  if (
    excluded(name) ||
    /(?:^|\/)(?:package-lock\.json|gradlew(?:\.bat)?)$/.test(name) ||
    /\.(?:sql|py|jar|lock|properties|svg|png|jpe?g|webp|ico|woff2?|toml|bat|sh)$/.test(
      name,
    )
  )
    return 'skip';
  if (/^backend\/src\/.*\.java$/.test(name)) return 'java';
  if (
    rootFiles.includes(name) ||
    /^\.(?:github\/workflows\/.*\.ya?ml|codex\/hooks\.json|vscode\/.*\.json)$/.test(
      name,
    )
  )
    return 'prettier';
  if (/^(?:docs|harness|work)\/.*\.(?:md|json|ya?ml)$/.test(name))
    return 'prettier';
  if (/^scripts\/.*\.(?:[cm]?js|json)$/.test(name)) return 'prettier';
  if (
    /^frontend\/(?:src\/.*\.(?:[cm]?[jt]sx?|css|json|html)|[^/]+\.(?:[cm]?[jt]s|json|html|css))$/.test(
      name,
    )
  )
    return 'prettier';
  if (/^backend\/src\/.*\.ya?ml$/.test(name)) return 'prettier';
  return 'unknown';
}

export async function safeFile(root, input) {
  const name = normalize(input);
  if (
    preserved.includes(name.split('/')[0].toLowerCase()) ||
    name
      .split('/')
      .some(
        (p) => p.toLowerCase() === '.git' || p.toLowerCase().startsWith('.env'),
      )
  )
    throw Error('Preserved/private file is outside quality scope.');
  const base = path.resolve(root);
  let cursor = base;
  for (const part of name.split('/')) {
    cursor = path.join(cursor, part);
    try {
      if ((await fs.lstat(cursor)).isSymbolicLink())
        throw Error('Symlink/junction requires review.');
    } catch (e) {
      if (e.code !== 'ENOENT') throw e;
    }
  }
  if (!cursor.startsWith(base + path.sep))
    throw Error('File escapes the workspace.');
  return cursor;
}

export async function collectFiles(root, { docs = false } = {}) {
  const found = [];
  async function visit(name) {
    if (excluded(name)) return; // Filter names before stat/readdir, including preservation roots.
    const file = await safeFile(root, name);
    let stat;
    try {
      stat = await fs.lstat(file);
    } catch (e) {
      if (e.code === 'ENOENT') return;
      throw e;
    }
    if (stat.isDirectory()) {
      for (const entry of await fs.readdir(file))
        await visit(name + '/' + entry);
    } else if (stat.isFile() && ['prettier', 'java'].includes(formatKind(name)))
      found.push(name);
  }
  for (const name of roots) {
    if (
      docs &&
      !rootFiles.includes(name) &&
      !['docs', 'harness', 'work'].includes(name)
    )
      continue;
    await visit(name);
  }
  return [...new Set(found)].sort();
}

export function classifyChanges(names) {
  const result = Object.fromEntries(areas.map((x) => [x, false]));
  const all = () => Object.fromEntries(areas.map((x) => [x, true]));
  for (const input of names) {
    let name;
    try {
      name = normalize(input);
    } catch {
      return all();
    }
    if (preserved.includes(name.split('/')[0].toLowerCase())) continue;
    if (name.startsWith('frontend/')) result.frontend = true;
    else if (/^(?:backend|db)\//.test(name)) result.backend = true;
    else if (
      /^(?:docs|harness|work)\//.test(name) ||
      ['AGENTS.md', 'README.md', 'STRUCTURE.md'].includes(name)
    )
      result.docs = true;
    else return all(); // Shared scripts/hooks/config/locks and unclassified paths.
  }
  return result;
}
