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
            index_document(writer, link[0], link[1], link[2]);
        writer.commit();
    }

    public static List<String[]> get_db_data(String dbFile) {
        List<String[]> dbResults = new ArrayList<String[]>();
        try {
            Connection connection = DriverManager.getConnection("jdbc:sqlite:" + dbFile);
            Statement statement = connection.createStatement();

            ResultSet rs = statement.executeQuery("SELECT * FROM PAGES");
            while (rs.next()) {
                String[] dbResult = new String[3];
                dbResult[0] = rs.getString("url");
                dbResult[1] = rs.getString("title");
                dbResult[2] = rs.getString("html");
                dbResults.add(dbResult);
            }
            statement.close();
            connection.close();
            return dbResults;

        } catch (Exception e) {
            System.out.println("[Indexer] [get_db_data] EXCEPTION OCCURRED: " + e.getMessage());
            return null;
        }
    }

    public static void index_document(IndexWriter writer, String url, String title, String html) throws IOException {
        Document doc = new Document();
        doc.add(new StringField("url", url, Field.Store.YES));
        doc.add(new TextField("title", title, Field.Store.YES));
        doc.add(new TextField("html", html, Field.Store.YES));
        writer.addDocument(doc);
    }
}
