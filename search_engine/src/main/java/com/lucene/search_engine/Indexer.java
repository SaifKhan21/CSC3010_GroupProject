package com.lucene.search_engine;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
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
import java.util.ArrayList;
import java.util.List;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class Indexer {

    public static void index_links(IndexWriter writer, List<String[]> links) throws IOException, ParseException {
        // Clears all previously existing indexes first
        writer.deleteAll();

        for (String[] link : links)
            index_document(writer, link[0], link[1]);
        writer.commit();
    }

    public static List<String[]> get_db_data(String dbFile) {
        List<String[]> dbResults = new ArrayList<String[]>();
        try {
            Connection connection = DriverManager.getConnection("jdbc:sqlite:" + dbFile);
            Statement statement = connection.createStatement();

            ResultSet rs = statement.executeQuery("SELECT * FROM PAGES");
            while (rs.next()) {
                String[] dbResult = new String[2];
                dbResult[0] = rs.getString("url");
                dbResult[1] = rs.getString("html");
                dbResults.add(dbResult);
            }
            statement.close();
            connection.close();

        } catch (Exception e) {
            System.out.println("[get_db_data] EXCEPTION OCCURRED: " + e.getMessage());
        }
        return dbResults;
    }

    public static void index_document(IndexWriter writer, String url, String content) throws IOException {
        Document doc = new Document();
        doc.add(new StringField("url", url, Field.Store.YES));
        doc.add(new TextField("content", content, Field.Store.YES));
        writer.addDocument(doc);
    }

    public static void basic_indexing() throws IOException, ParseException {
        NIOFSDirectory indexDir = new NIOFSDirectory(Paths.get("index"));
        Analyzer analyzer = new EnglishAnalyzer();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter writer = new IndexWriter(indexDir, config);
        writer.deleteAll(); // Clears all previously existing documents in writer

        index_document(writer, "Document 1", "This is the amenity content of document 1.");
        index_document(writer, "Document 2", "This is some other amenities content of document 2.");
        index_document(writer, "Document 3", "This is another amenity content of document 3.");
        writer.commit();
        //writer.close(); // Reader can't access if closed, writer is closed later after reader is done

        //IndexSearcher searcher = new IndexSearcher(writer.getReader()); // Doesn't work, have to use below method
        IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(writer));
        Query query = new QueryParser("content", analyzer).parse("amenities");
        ScoreDoc[] hits = searcher.search(query, 10).scoreDocs;
        writer.close();

        System.out.println("Found " + hits.length + " hits:");
        for (ScoreDoc hit : hits) {
            Document doc = searcher.doc(hit.doc);
            System.out.println("Title: " + doc.get("title"));
            System.out.println("Content: " + doc.get("content"));
        }
    }
}
