"use client";

import { useState } from "react";

// Define the type for search results
interface SearchResult {
    url: string;
    title: string,
    html: string;
}

export default function Home() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [loading, setLoading] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query) return;

        try {
            const encodedQuery = query.replace(" ", "%20");
            setError("Searching...");
            const res = await fetch(`http://localhost:8080/query?q=${encodedQuery}`);
            const text = await res.text();
            setLoading(null);
            // Log the response text to analyze the issue
            // console.log("Response text: ", text);
            // Parse the response text to extract the results
            const parsedResults = parseResults(text);
            setResults(parsedResults);
            setError(null);
            setCurrentPage(1); // Reset to the first page on new search
        } catch (error) {
            console.error("Error fetching search results:", error);
            setError(
                "Error fetching search results. Please check the console for more details."
            );
            setResults([]);
        } 
    };

    const performIndex = async (e: React.FormEvent) => {
        e.preventDefault();

        
        try {
            setError("Indexing...");
            const res = await fetch(`http://localhost:8080/index_db`);
            // Log the response text to analyze the issue
            console.log("Indexing...");

            setLoading(null);
            // Parse the response text to extract the results
            setError(
                "Index successful!"
            );
            setCurrentPage(1); // Reset to the first page on new search
            setResults([]); // Set results to blank
        } catch (error) {
            console.error("Error performing indexing:", error);
            setError(
                "Error performing indexing. Please check the console for more details."
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
            const titleMatch = line.match(/Title: (.*)<br>/);
            const htmlMatch = line.match(/Content: (.*)/);

            if (urlMatch && titleMatch && htmlMatch) {
                results.push({
                    url: urlMatch[1],
                    title: titleMatch[1],
                    html: htmlMatch[1],
                });
            }
        });

        return results;
    };

    // Pagination logic
    const resultsPerPage = 10;
    const totalPages = Math.ceil(results.length / resultsPerPage);
    const currentResults = results.slice(
        (currentPage - 1) * resultsPerPage,
        currentPage * resultsPerPage
    );

    const handlePageChange = (pageNumber: number) => {
        setCurrentPage(pageNumber);
    };

    const renderPaginationButtons = () => {
        const maxVisiblePages = 8;
        const startPage = Math.max(
            Math.min(
                currentPage - Math.floor(maxVisiblePages / 2),
                totalPages - maxVisiblePages
            ),
            1
        );

        const endPage = Math.min(startPage + maxVisiblePages - 1, totalPages);
        const paginationButtons = [];

        for (let i = startPage; i <= endPage; i++) {
            paginationButtons.push(
                <button
                    key={i}
                    onClick={() => handlePageChange(i)}
                    className={`mx-1 px-3 py-1 rounded ${
                        i === currentPage
                            ? "bg-blue-500 text-white"
                            : "bg-gray-300 text-gray-700"
                    }`}
                >
                    {i}
                </button>
            );
        }

        return (
            <>
                {startPage > 1 && (
                    <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        className="mx-1 px-3 py-1 rounded bg-gray-300 text-gray-700"
                    >
                        Prev
                    </button>
                )}
                {paginationButtons}
                {endPage < totalPages && (
                    <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        className="mx-1 px-3 py-1 rounded bg-gray-300 text-gray-700"
                    >
                        Next
                    </button>
                )}
            </>
        );
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
                    className="px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    Search
                </button>
                <button
                    onClick={performIndex}
                    className="px-4 py-2 bg-green-500 text-white rounded-r-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                    Index
                </button>
            </form>
            {error && (
                <div className="mt-4 w-full max-w-xl text-red-500">{error}</div>
            )}
            <div className="mt-8 w-full max-w-xl">
                {currentResults.length > 0 ? (
                    <>
                    <p className="text-gray-700 mb-4">
                    {results.length} {results.length === 1 ? 'result' : 'results'} found
                    </p>
                    {currentResults.map((result, index) => (
                        <div
                            key={index}
                            className="mb-4 p-4 bg-white rounded-lg shadow-md"
                        >
                            <a
                                href={result.url}
                                className="text-xl font-semibold text-blue-600 hover:underline"
                            >
                                {result.title}
                            </a>
                            <br/>
                            {result.html}
                        </div>
                    ))}
                    </>
                ) : (
                    <p className="text-gray-500">No results found</p>
                )}
            </div>
            {results.length > resultsPerPage && (
                <div className="flex flex-row flex-wrap my-4 px-10 w-full gap-2 justify-center">
                    {renderPaginationButtons()}
                </div>
            )}
        </div>
    );
}
