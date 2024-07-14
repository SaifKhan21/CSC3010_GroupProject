package com.lucene.search_engine;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.store.NIOFSDirectory;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

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
    @RequestMapping("/query")
    public String query_index() throws IOException, ParseException {
        String user_query = "tom hanks";

        try {
            IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(writer));
            Query query = new QueryParser("content", analyzer).parse(user_query);
            ScoreDoc[] hits = searcher.search(query, 30).scoreDocs;

            String result = "";
            result += "Found " + hits.length + " hits:<br>";
            for (ScoreDoc hit : hits) {
                Document doc = searcher.doc(hit.doc);
                result += "URL: " + doc.get("url") + "<br>";

                String content = doc.get("content");
                String shortenedContent = content.substring(0, Math.min(content.length(), 30));
                result += "Content: " + shortenedContent + "<br><br>";
            }
            return result;
        } catch (Exception e) {
            return "[query_index] EXCEPTION OCCURRED: " + e.getMessage();
        }
    }
}
