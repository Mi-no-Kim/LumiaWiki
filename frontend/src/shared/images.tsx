import { useState } from 'react';

export function imageUrl(path: string | null | undefined, base = import.meta.env.BASE_URL): string | null {
  if (!path || !base.startsWith('/') || base.startsWith('//') || !base.endsWith('/')) return null;
  const parts = path.split('/');
  if (parts.some(part => !part || part === '.' || part === '..' || /[:?#\\%\u0000-\u001f]/.test(part))) return null;
  return `${base}images/${parts.map(encodeURIComponent).join('/')}`;
}

function ImageSource({ source, alt }: { source: string | null; alt: string }) {
  const [failed, setFailed] = useState(false);
  const placeholder = `${import.meta.env.BASE_URL}images/placeholder.svg`;
  return <img src={failed ? placeholder : source ?? placeholder} alt={alt} onError={() => setFailed(true)} />;
}

export function CommonImage({ path, alt }: { path?: string | null; alt: string }) {
  const source = imageUrl(path);
  return <ImageSource key={source ?? 'placeholder'} source={source} alt={alt} />;
}
