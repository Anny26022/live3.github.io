import { NextResponse } from 'next/server';
// Need to use require for these CJS modules in an ES module context
const GoogleNewsScraper = require('google-news-scraper'); 
const Sentiment = require('sentiment');

// Initialize sentiment analyzer
const sentiment = new Sentiment();

// Define the structure for a news article, including sentiment
interface NewsArticle {
    title: string;
    description: string | null; // Scraper might not always provide description
    url: string;
    publishedAt: string; // Keep as ISO string
    source?: string; 
    sentimentScore?: number; // VADER-like compound score
    sentimentLabel?: 'Positive' | 'Negative' | 'Neutral';
}

// Helper function to map sentiment score to label
function getSentimentLabel(score: number): 'Positive' | 'Negative' | 'Neutral' {
    if (score > 0.5) return 'Positive'; // Adjust thresholds as needed
    if (score < -0.5) return 'Negative';
    return 'Neutral';
}

async function fetchNewsForSymbol(symbol: string): Promise<NewsArticle[]> {
    console.log(`Fetching real news for: ${symbol}`);
    try {
        // Configure scraper - let's keep it simple for now
        const articles = await GoogleNewsScraper({ 
            searchTerm: symbol,
            prettyURLs: false, // Get actual URLs
            queryVars: {
                hl: 'en-US', // Language
                gl: 'US',   // Country
                ceid: 'US:en' // Combine
            },
            timeframe: '7d', // Match python default '7d'
            maxResults: 15 // Fetch a few more initially
        });

        // Process articles: map, analyze sentiment
        const processedArticles: NewsArticle[] = articles.map((article: any) => {
            const analysis = sentiment.analyze(article.title || ''); // Analyze title
            const sentimentScore = analysis.comparative; // Use comparative score (similar to VADER compound)
            const sentimentLabel = getSentimentLabel(sentimentScore);

            return {
                title: article.title,
                description: article.subtitle || null, // Use subtitle as description if available
                url: article.link,
                publishedAt: article.isoDate || new Date().toISOString(), // Use ISO date if available, else fallback
                source: article.source || 'Unknown Source',
                sentimentScore: sentimentScore,
                sentimentLabel: sentimentLabel,
            };
        });
        
        // Sort by date descending (latest first)
        processedArticles.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());

        return processedArticles.slice(0, 10); // Limit to 10 results for the API response

    } catch (error: any) {
        console.error(`Error scraping news for ${symbol}:`, error);
        // Don't throw, return empty array or handle differently?
        // For now, let the route handler catch and return 500
        throw new Error(`Failed to scrape news: ${error.message}`);
    }
}

export async function GET(
    request: Request,
    { params }: { params: { symbol: string } }
) {
    const symbol = params.symbol;

    if (!symbol) {
        return NextResponse.json({ error: 'Symbol parameter is required' }, { status: 400 });
    }

    try {
        const newsArticles = await fetchNewsForSymbol(symbol.toUpperCase());
        return NextResponse.json(newsArticles);

    } catch (error: any) {
        console.error(`API Route Error (News for ${symbol}):`, error);
        return NextResponse.json({ error: error.message || 'Failed to fetch news' }, { status: 500 });
    }
} 