import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
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

public class Main {
    public static void main(String[] args) throws IOException, ParseException {
        System.out.println("Hello and welcome!");

        NIOFSDirectory indexDir = new NIOFSDirectory(Paths.get("index"));
        Analyzer analyzer = new StandardAnalyzer();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter writer = new IndexWriter(indexDir, config);
        writer.deleteAll(); // Clears all previously existing documents in writer

        index_document(writer, "Document 1", "This is the content of document 1.");
        index_document(writer, "Document 2", "This is some other content of document 2.");
        writer.commit();
        //writer.close(); // Reader can't access if closed, writer is closed later after reader is done

        //IndexSearcher searcher = new IndexSearcher(writer.getReader()); // Doesn't work, have to use below method
        IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(writer));
        Query query = new QueryParser("content", analyzer).parse("content");
        ScoreDoc[] hits = searcher.search(query, 10).scoreDocs;
        writer.close();

        System.out.println("Found " + hits.length + " hits:");
        for (ScoreDoc hit : hits) {
            Document doc = searcher.doc(hit.doc);
            System.out.println("Title: " + doc.get("title"));
            System.out.println("Content: " + doc.get("content"));
        }
    }

    public static void index_document(IndexWriter writer, String title, String content) throws IOException {
        Document doc = new Document();
        doc.add(new StringField("title", title, Field.Store.YES));
        doc.add(new TextField("content", content, Field.Store.YES));
        writer.addDocument(doc);
    }
}