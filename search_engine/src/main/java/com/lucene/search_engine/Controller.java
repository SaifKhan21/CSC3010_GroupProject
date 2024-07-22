package com.lucene.search_engine;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.store.NIOFSDirectory;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

@RestController
public class Controller {
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
        if (dbLinks == null)
            return "Error occurred when getting database data.";

        Indexer.index_links(writer, dbLinks);
        return "DB has been successfully indexed.";
    }

    // Queries the index with a user query string
    @RequestMapping("/query")
    public String search_for_results(@RequestParam("q") String userQuery) throws IOException, ParseException {
        userQuery = userQuery.replaceAll("%20", " ");
        String queryResult = Queryer.query_index(userQuery, analyzer, writer);
        if (queryResult == null)
            return "Error occurred when searching for results.";

        return queryResult;
    }
}
