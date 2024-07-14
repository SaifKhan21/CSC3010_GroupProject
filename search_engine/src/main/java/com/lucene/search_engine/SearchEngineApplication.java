package com.lucene.search_engine;

import org.apache.lucene.queryparser.classic.ParseException;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.IOException;

@SpringBootApplication
public class SearchEngineApplication {

	public static void main(String[] args) throws IOException, ParseException {
		Queryer.build_components();
		SpringApplication.run(SearchEngineApplication.class, args);
	}
}
