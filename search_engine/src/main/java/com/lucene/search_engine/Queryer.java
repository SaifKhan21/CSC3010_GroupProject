package com.lucene.search_engine;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.NIOFSDirectory;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Queryer {
    static NIOFSDirectory indexDir;
    static Analyzer analyzer;
    static IndexWriter writer;

    public static void build_components() throws IOException, ParseException {
        indexDir = new NIOFSDirectory(Paths.get("index"));
        analyzer = new EnglishAnalyzer();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        writer = new IndexWriter(indexDir, config);
    }

    // Builds an index from the database file
    @RequestMapping("/index_db")
    public String index_database() throws IOException, ParseException {
        List<String[]> dbLinks = Indexer.get_db_data("imdb_data.db");
        Indexer.index_links(writer, dbLinks);

        return "DB has been successfully indexed!";
    }


    // Queries the index with a user query string
    //@CrossOrigin(origins = "http://localhost:3000") // Allow requests from this origin
    @RequestMapping("/query")
    public String queryIndex() throws IOException, ParseException {
        String user_query = "Jurassic World";
        try {
            DirectoryReader reader = DirectoryReader.open(writer);
            IndexSearcher searcher = new IndexSearcher(reader);
            searcher.setSimilarity(new BM25Similarity()); // Set BM25Similarity for searching

            // Boosting the content field in the query
            QueryParser parser = new QueryParser("content", analyzer);
            parser.setDefaultOperator(QueryParser.Operator.AND);
            Query query = parser.parse(user_query);

            BooleanQuery boostedQuery = new BooleanQuery.Builder()
                .add(new BooleanClause(query, BooleanClause.Occur.SHOULD))
                .build();

            ScoreDoc[] hits = searcher.search(boostedQuery, 1000).scoreDocs;

            StringBuilder result = new StringBuilder();
            result.append("Found ").append(hits.length).append(" hits:<br>");
            for (ScoreDoc hit : hits) {
                Document doc = searcher.doc(hit.doc);
                result.append("URL: ").append(doc.get("url")).append("<br>");
                String content = doc.get("content");
                String shortenedContent = content.substring(0, Math.min(content.length(), 30));
                result.append("Content: ").append(shortenedContent).append("<br><br>");
            }
            reader.close();
            return result.toString();
        } catch (Exception e) {
            return "[queryIndex] EXCEPTION OCCURRED: " + e.getMessage();
        }
    }
}
