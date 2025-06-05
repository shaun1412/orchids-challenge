'use client';

import { useState } from 'react';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [clonedHtml, setClonedHtml] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setClonedHtml('');

    try {
      const response = await fetch('http://localhost:8000/api/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to clone website');
      }

      const data = await response.json();

      // Process HTML to make image URLs absolute
      const parser = new DOMParser();
      const doc = parser.parseFromString(data.html, 'text/html');

      const imgTags = doc.querySelectorAll('img');
      imgTags.forEach(img => {
        const src = img.getAttribute('src');
        if (src) {
          try {
            // Check if src is already absolute or data URL
            if (!src.startsWith('http://') && !src.startsWith('https://') && !src.startsWith('//') && !src.startsWith('data:')) {
              // Construct absolute URL using the original website URL
              const absoluteUrl = new URL(src, url).href; // Use the 'url' state variable
              img.setAttribute('src', absoluteUrl);
            }
          } catch (e) {
            console.error('Error converting relative URL:', src, e);
            // Optionally remove the image or set a placeholder if conversion fails
            // img.remove();
          }
        }
      });

      const modifiedHtml = new XMLSerializer().serializeToString(doc);
      setClonedHtml(modifiedHtml);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={`min-h-screen p-8 ${inter.className}`}>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">Website Cloner</h1>
        
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-4">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter website URL (e.g., https://example.com)"
              className="flex-1 p-2 border rounded"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
            >
              {loading ? 'Cloning...' : 'Clone Website'}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-4 mb-4 text-red-700 bg-red-100 rounded">
            {error}
          </div>
        )}

        {clonedHtml && (
          <div className="border rounded p-4">
            <h2 className="text-2xl font-semibold mb-4">Cloned Website Preview</h2>
            <div className="border rounded overflow-auto max-h-[600px]">
              <iframe
                srcDoc={clonedHtml}
                className="w-full h-[600px]"
                title="Cloned Website"
              />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
