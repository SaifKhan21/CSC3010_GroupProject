from org.apache.lucene.analysis.standard.StandardAnalyzer import StandardAnalyzer
from org.apache.lucene.document import Document, StringField, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from java.nio.file import Paths

indexDir = NIOFSDirectory(Paths.get("index"))
analyzer = StandardAnalyzer()
config = IndexWriterConfig(analyzer)
writer = IndexWriter(indexDir, config)

def index_document(title, content):
    doc = Document()
    doc.add(StringField("title", title, Field.Store.YES))
    doc.add(TextField("content", content, Field.Store.YES))
    writer.addDocument(doc)

index_document("Document 1", "This is the content of document 1.")
index_document("Document 2", "This is some other content of document 2.")

writer.commit()
writer.close()

searcher = IndexSearcher(writer.getReader())
query = QueryParser("content", analyzer).parse("content")
hits = searcher.search(query, 10).scoreDocs

print("Found %d hits:" % len(hits))
for hit in hits:
    doc = searcher.doc(hit.doc)
    print("Title:", doc.get("title"))
    print("Content:", doc.get("content"))