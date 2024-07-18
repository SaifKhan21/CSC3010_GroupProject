import hashlib
import gspread
import numpy as np
import utility
from sklearn.feature_extraction.text import TfidfVectorizer

class CrawlerDataSheet:
    '''
    This class is used to interact with the 'crawler_data' sheet in the Google Sheets database.
    
    Headers of the 'crawler_data' sheet:
    - url_hash: MD5 hash of the URL
    - url: URL of the webpage
    - datetime: Datetime of the crawl (%Y-%m-%d %H:%M:%S)
    - title: Title of the webpage
    - content_type: Content type of the webpage
    - content: Content of the webpage
    - content_length: Length of the content
    - content_hash: MD5 hash of the content
    - response_time: Time to crawl the webpage
    - metadata: Metadata of the webpage
    - error_code: Error code of the crawl
    '''
    # Headers:
    # url_hash	url	datetime	title	content-type	content	content_length	content_hash	response_time	metadata	error_code
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('crawler_data')
        self.tfidf_vectorizer = TfidfVectorizer()
        self.url_tfidf_vectorizer = TfidfVectorizer()
        self.data_dict = self.get_all_data_dict()
        self.update_local_data_and_matrices()

    def get_all_data(self):
        ''' Returns all the data in the 'crawler_data' sheet '''
        return self.sheet.get_all_records()

    def get_all_data_dict(self):
        ''' Returns a dictionary of url_hash: data pairs '''
        records = self.get_all_data()
        return {record['url_hash']: record for record in records}

    def update_local_data_and_matrices(self):
        ''' Updates the local data dictionary and TF-IDF matrices.
            This function should be called after adding new data to the sheet.
            The TF-IDF matrices are used to check for similarity between new and existing data.
        '''
        self.data_dict = self.get_all_data_dict()
        self.content_tfidf_matrix = self.compute_content_tfidf_matrix()
        self.url_tfidf_matrix = self.compute_url_tfidf_matrix()

    def compute_content_tfidf_matrix(self):
        ''' Computes the TF-IDF matrix for the content of the webpages 
            
            Returns:
                scipy.sparse.csr_matrix: TF-IDF matrix of the content
        '''
        contents = [record['content'] for record in self.data_dict.values()]
        if contents:
            return self.tfidf_vectorizer.fit_transform(contents)
        return None

    def compute_url_tfidf_matrix(self):
        ''' Computes the TF-IDF matrix for the URLs of the webpages
        
            Returns:
                scipy.sparse.csr_matrix: TF-IDF matrix of the URLs
        '''
        urls = [record['url'] for record in self.data_dict.values()]
        if urls:
            return self.url_tfidf_vectorizer.fit_transform(urls)
        return None

    def get_data_by_url(self, url_hash=None, url=None):
        ''' Returns the data with the given URL or URL hash
        
            Args:
                url_hash (explicitly stated): str, URL hash of the webpage
                url (explicitly stated): str, URL of the webpage
                
            Returns:
                dict: Data with the given URL or URL hash
        '''
        if url_hash:
            return self.data_dict.get(url_hash, None)
        if url:
            for record in self.data_dict.values():
                if record['url'] == url:
                    return record
        return None

    def add_data(self, url_hash, url, datetime, title, content_type, content, content_length, content_hash, response_time, metadata, error_code):
        ''' Adds new data to the 'crawler_data' sheet if it does not already exist
        
            Args:
                url_hash: str, URL hash of the webpage
                url: str, URL of the webpage
                datetime: str, Datetime of the crawl (%Y-%m-%d %H:%M:%S)
                title: str, Title of the webpage
                content_type: str, Content type of the webpage
                content: str, Content of the webpage
                content_length: int, Length of the content
                content_hash: str, MD5 hash of the content
                response_time: float, Time to crawl the webpage
                metadata: str, Metadata of the webpage
                error_code: int, Error code of the crawl

            Returns:
                bool: True if data was added, False otherwise
        '''
        self.update_local_data_and_matrices()  # Refresh local data and matrices

        if self.get_data_by_url(url_hash=url_hash):
            print(f'Data already exists in the crawler data sheet: {url}')
            return False

        new_content_vector = self.tfidf_vectorizer.transform([content])
        new_url_vector = self.url_tfidf_vectorizer.transform([url])

        if self.content_tfidf_matrix is not None:
            content_similarities = utility.cosine_similarity(new_content_vector, self.content_tfidf_matrix)
            max_content_similarity = np.max(content_similarities)
            if max_content_similarity > 0.8:
                print(f'Content is too similar to existing data in the crawler data sheet: {url}')
                return False

        if self.url_tfidf_matrix is not None:
            url_similarities = utility.cosine_similarity(new_url_vector, self.url_tfidf_matrix)
            max_url_similarity = np.max(url_similarities)
            if max_url_similarity > 0.8:
                print(f'URL is too similar to existing data in the crawler data sheet: {url}')
                return False

        self.sheet.append_row([
            url_hash,
            url,
            datetime,
            title,
            content_type,
            content,
            content_length,
            content_hash,
            response_time,
            metadata,
            error_code
        ])
        print(f'Added new data to the crawler data sheet: {url}')

        # Update the local data and TF-IDF matrices
        self.update_local_data_and_matrices()

        return True
