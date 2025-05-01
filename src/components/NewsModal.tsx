'use client';

import React, { useState, useEffect } from 'react';

// Update interface to include sentiment fields
interface NewsArticle {
    title: string;
    description: string | null;
    url: string;
    publishedAt: string;
    source?: string;
    sentimentScore?: number;
    sentimentLabel?: 'Positive' | 'Negative' | 'Neutral';
}

interface NewsModalProps {
    symbol: string | null; // Symbol to fetch news for
    isOpen: boolean;
    onClose: () => void;
}

// Helper function to get sentiment emoji
function getSentimentEmoji(label?: 'Positive' | 'Negative' | 'Neutral'): string {
    switch (label) {
        case 'Positive': return '😊';
        case 'Negative': return '😞';
        case 'Neutral': return '😐';
        default: return '' ; // No emoji if undefined
    }
}

export default function NewsModal({ symbol, isOpen, onClose }: NewsModalProps) {
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Fetch news only when the modal is opened and a symbol is provided
        if (isOpen && symbol) {
            const fetchNews = async () => {
                setIsLoading(true);
                setError(null);
                setNews([]); // Clear previous news
                try {
                    // Use encodeURIComponent for symbols that might contain special characters
                    const encodedSymbol = encodeURIComponent(symbol);
                    const response = await fetch(`/api/news/${encodedSymbol}`);
                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.error || `Failed to fetch news (${response.status})`);
                    }
                    const data: NewsArticle[] = await response.json();
                    setNews(data);
                } catch (err: any) {
                    setError(err.message);
                    console.error("News fetch error:", err);
                } finally {
                    setIsLoading(false);
                }
            };

            fetchNews();
        }
    }, [isOpen, symbol]); // Dependency array: refetch when modal opens or symbol changes

    if (!isOpen || !symbol) {
        return null; // Don't render anything if modal is closed or no symbol
    }

    // Function to format date nicely
    const formatDate = (dateString: string) => {
        try {
            return new Date(dateString).toLocaleString(undefined, {
                dateStyle: 'medium',
                timeStyle: 'short'
            });
        } catch (e) {
            return dateString; // Fallback
        }
    };

    return (
        // Basic Modal structure using fixed position and backdrop
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm"
            onClick={onClose} // Close modal on backdrop click
        >
            <div
                className="bg-gray-800 text-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col"
                onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal content
            >
                {/* Modal Header */}
                <div className="flex justify-between items-center p-4 border-b border-gray-700">
                    <h2 className="text-xl font-semibold">📰 News for {symbol.toUpperCase()}</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white text-2xl font-bold leading-none"
                        aria-label="Close modal"
                    >
                        &times;
                    </button>
                </div>

                {/* Modal Body */} 
                <div className="p-5 overflow-y-auto">
                    {isLoading && <p className="text-center text-gray-400">Loading news...</p>}
                    {error && <p className="text-center text-red-500">Error: {error}</p>}
                    {!isLoading && !error && news.length === 0 && (
                        <p className="text-center text-gray-500">No recent news found for {symbol}.</p>
                    )}
                    {!isLoading && !error && news.length > 0 && (
                        <ul className="space-y-4">
                            {news.map((article, index) => (
                                <li key={index} className="border-b border-gray-700 pb-3 last:border-b-0">
                                    <a
                                        href={article.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block hover:bg-gray-700 p-2 rounded transition-colors"
                                    >
                                         {/* Display Sentiment Emoji before Title */}
                                         <h3 className="text-md font-semibold text-blue-400 mb-1">
                                            {getSentimentEmoji(article.sentimentLabel)} {article.title}
                                        </h3>
                                        {article.description && (
                                            <p className="text-sm text-gray-300 mb-1.5">{article.description}</p>
                                        )}
                                        <div className="text-xs text-gray-500 flex justify-between items-center">
                                            <span>{article.source || 'Source Unknown'}</span>
                                             {/* Display Sentiment Label next to date */}
                                             <span className="flex items-center">
                                                {article.sentimentLabel && (
                                                    <span 
                                                        className={`mr-2 px-1.5 py-0.5 rounded text-xs font-medium 
                                                            ${article.sentimentLabel === 'Positive' ? 'bg-green-800 text-green-100' : 
                                                            article.sentimentLabel === 'Negative' ? 'bg-red-800 text-red-100' : 
                                                            'bg-yellow-800 text-yellow-100'}
                                                        `}
                                                    >
                                                        {article.sentimentLabel}
                                                    </span>
                                                )}
                                                {formatDate(article.publishedAt)}
                                            </span>
                                        </div>
                                    </a>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
                 {/* Modal Footer (Optional) */} 
                 <div className="p-3 border-t border-gray-700 text-right">
                      <button 
                         onClick={onClose}
                         className="px-4 py-1.5 rounded bg-gray-600 hover:bg-gray-500 text-white text-sm"
                     >
                         Close
                     </button>
                 </div>
            </div>
        </div>
    );
} 