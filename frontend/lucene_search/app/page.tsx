"use client";

import { useState } from "react";

// Define the type for search results
interface SearchResult {
    url: string;
    content: string;
}

export default function Home() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query) return;

        try {
            const res = await fetch(`http://localhost:8080/query?q=${query}`);
            const text = await res.text();

            // Log the response text to analyze the issue
            // console.log("Response text:", text);

            // Parse the response text to extract the results
            const parsedResults = parseResults(text);
            setResults(parsedResults);
            setError(null);
        } catch (error) {
            console.error("Error fetching search results:", error);
            setError(
                "Error fetching search results. Please check the console for more details."
            );
            setResults([]);
        }
    };

    // Function to parse the response text
    const parseResults = (text: string): SearchResult[] => {
        const lines = text.split("<br><br>");
        const results: SearchResult[] = [];

        lines.forEach((line) => {
            const urlMatch = line.match(/URL: (.*?)<br>/);
            const contentMatch = line.match(/Content: (.*)/);

            if (urlMatch && contentMatch) {
                results.push({
                    url: urlMatch[1],
                    content: contentMatch[1],
                });
            }
        });

        return results;
    };

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
            <h1 className="text-4xl font-bold mb-8">Search Engine</h1>
            <form
                onSubmit={handleSearch}
                className="w-full max-w-xl flex items-center"
            >
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Search..."
                />
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    Search
                </button>
            </form>
            {error && (
                <div className="mt-4 w-full max-w-xl text-red-500">{error}</div>
            )}
            <div className="mt-8 w-full max-w-xl">
                {results.length > 0 ? (
                    results.map((result, index) => (
                        <div
                            key={index}
                            className="mb-4 p-4 bg-white rounded-lg shadow-md"
                        >
                            <a
                                href={result.url}
                                className="text-xl font-semibold text-blue-600 hover:underline"
                            >
                                {result.content}
                            </a>
                            {/* <p className="text-gray-700">{result.content}</p> */}
                        </div>
                    ))
                ) : (
                    <p className="text-gray-500">No results found</p>
                )}
            </div>
        </div>
    );
}
