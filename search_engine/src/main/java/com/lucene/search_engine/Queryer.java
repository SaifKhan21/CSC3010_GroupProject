package com.lucene.search_engine;

import java.io.IOException;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.search.similarities.BM25Similarity;

public class Queryer {

    public static String query_index(String user_query, Analyzer analyzer, IndexWriter writer) throws IOException, ParseException {
        try {
            DirectoryReader reader = DirectoryReader.open(writer);
            IndexSearcher searcher = new IndexSearcher(reader);
            // Set BM25Similarity as the ranking system
            searcher.setSimilarity(new BM25Similarity());

            // Setting the parser to check and parse query against the HTML field in the documents
            QueryParser htmlParser = new QueryParser("html", analyzer);
            Query htmlQuery = htmlParser.parse(user_query);
            Query boostedHtmlQuery = new BoostQuery(htmlQuery, 1f);

            // Gives a weighted multiplier for documents that match the query terms in the Title and HTML fields
            BooleanQuery boostedQuery = new BooleanQuery.Builder()
                .add(new BooleanClause(boostedHtmlQuery, BooleanClause.Occur.SHOULD))
                .build();

            ScoreDoc[] hits = searcher.search(boostedQuery, 100).scoreDocs;

            StringBuilder result = new StringBuilder();
            result.append("<b>FOUND ").append(hits.length).append(" HITS:</b><br>");
            for (ScoreDoc hit : hits) {
                Document doc = searcher.doc(hit.doc);
                result.append("URL: ").append(doc.get("url")).append("<br>");
                result.append("Title: ").append(doc.get("title")).append("<br>");
                String html = doc.get("html");
                String shortenedContent = html.substring(0, Math.min(html.length(), 250));
                result.append("Content: ").append(shortenedContent).append("<br><br>");
            }
            reader.close();
            return result.toString();
        } catch (Exception e) {
            System.out.println("[Queryer] [query_index] EXCEPTION OCCURRED: " + e.getMessage());
            return null;
        }
    }
}
