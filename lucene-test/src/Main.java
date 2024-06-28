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

public class Main {
    public static void main(String[] args) throws IOException, ParseException {
        System.out.println("Hello and welcome!");

        NIOFSDirectory indexDir = new NIOFSDirectory(Paths.get("index"));
        Analyzer analyzer = new EnglishAnalyzer();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter writer = new IndexWriter(indexDir, config);

        // Comment out these lines if you don't want to rebuild the index
        List<String[]> dbLinks = Indexer.get_db_data("imdb_data.db");
        Indexer.index_links(writer, dbLinks);

        query_index(analyzer, writer, "imdb");
        //Indexer.basic_indexing();
    }

    public static void query_index(Analyzer analyzer, IndexWriter writer, String user_query) {
        try {
            IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(writer));
            Query query = new QueryParser("content", analyzer).parse(user_query);
            ScoreDoc[] hits = searcher.search(query, 30).scoreDocs;

            System.out.println("Found " + hits.length + " hits:");
            for (ScoreDoc hit : hits) {
                Document doc = searcher.doc(hit.doc);
                System.out.println("URL: " + doc.get("url"));

                String content = doc.get("content");
                String shortenedContent = content.substring(0, Math.min(content.length(), 30));
                System.out.println("Content: " + shortenedContent);
            }
        } catch (Exception e) {
            System.out.println("[query_index] EXCEPTION OCCURRED: " + e.getMessage());
        }
    }
}
