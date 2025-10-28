import json
import os
from pathlib import Path

import pymupdf
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore

from app.config import Settings
from app.dependencies.database import get_supabase_client

settings = Settings()


def extract_toc(file_path: str) -> tuple[list, int]:
    """
    Extracts the Table of Contents of a file
    """
    with pymupdf.open(file_path) as doc:
        toc = doc.get_toc(simple=True)
        total_pages = len(doc)
    return toc, total_pages


def build_page_chapter_map(toc: list, total_pages: int) -> dict:
    """
    Makes a dictionary that maps each page to its chapter number
    """
    if not toc:
        return {}
    page_to_chapter = {}
    chapter_pages = [(entry[2], entry[1]) for entry in toc if entry[0] == 1]
    chapter_pages.sort(key=lambda x: x[0])
    for i, (start_page, title) in enumerate(chapter_pages):
        end_page = chapter_pages[i + 1][0] - 1 if i + 1 < len(chapter_pages) else total_pages
        for page in range(start_page, end_page + 1):
            page_to_chapter[page] = title
    return page_to_chapter


def prepare_vector_db_docs(doc_folder: str) -> list[Document]:
    """
    Loads and splits PDF documents from a specified folder for vector database ingestion.

    Each PDF is processed using LangChain's PyPDFLoader and split into smaller chunks using
    RecursiveCharacterTextSplitter to prepare for embedding and storage.

    Parameters:
        doc_folder (str): The path to the folder containing PDF documents.

    Returns:
        list[Document]: A list of text-split Document objects ready for embedding.

    Notes:
        - Non-PDF files are ignored.
        - Errors during loading or splitting are caught and printed.
        - Returns an empty list if the folder does not exist.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        keep_separator='end',
        separators=['. ', '? ', '! ', '\n\n', '\n'],
    )
    docs = []
    if not os.path.isdir(doc_folder):
        print(f"Warning: Document folder '{doc_folder}' does not exist.")
        return []

    author_license_map = load_authors_licenses_mapping()
    for file in os.listdir(doc_folder):
        if file.endswith('.pdf'):
            file_path = os.path.join(doc_folder, file)
            try:
                print(f'📄 Processing document {file}...')
                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()

                toc, total_pages = extract_toc(file_path)
                page_chapter_map = build_page_chapter_map(toc, total_pages)

                doc_name = os.path.basename(file)
                license_name, author = author_license_map.get(doc_name, ['Unknown', 'Unknown'])

                if license_name == 'Unknown':
                    print(f"⚠️ No license found for '{doc_name}', defaulting to 'Unknown'.")
                else:
                    print(f"📄 '{doc_name}' assigned license: {license_name}")

                if author == 'Unknown':
                    print(f"⚠️ No author found for '{doc_name}', defaulting to 'Unknown'.")
                else:
                    print(f"📄 '{doc_name}' author: {author}")

                for doc in loaded_docs:
                    # Replacing null bytes as they lead to errors
                    doc.page_content = doc.page_content.replace('\u0000', '')
                    doc.metadata['licenseName'] = license_name
                    doc.metadata['author'] = author
                    doc.metadata['chapter'] = page_chapter_map.get(doc.metadata.get('page', 0))
                    doc.metadata.pop('source', None)

                splits = text_splitter.split_documents(loaded_docs)
                docs.extend(splits)
                print(f'✅ Successfully processed {file} with {len(splits)} chunks')
            except Exception as e:
                print(f'❌ Error processing {file_path}: {e}')

    print(f'✅ Prepared {len(docs)} document chunks for vector DB.')
    return docs


def format_docs(docs: list[Document]) -> str:
    """
    Formats a list of Document objects into a single string, joining their contents.

    Parameters:
        docs (list[Document]): A list of LangChain Document objects.

    Returns:
        str: A single string containing the concatenated contents of all documents,
             separated by double newlines.
    """
    return '\n\n'.join([doc.page_content for doc in docs])


def format_docs_with_metadata(docs: list[Document]) -> tuple[str, list[dict]]:
    """
    Formats a list of Document objects into a single string, joining their contents,
    and collect their metadata together

    Parameters:
        docs (list[Document]): A list of LangChain Document objects.

    Returns:
        tuple[str, list[dict]]: A tuple of:
        1) A single string containing the concatenated contents of all documents,
             separated by double newlines
        2) The documents' metadata in an array of dicts
    """
    return '\n\n'.join([doc.page_content for doc in docs]), [
        {
            'quote': doc.page_content or '',
            'page': doc.metadata.get('page'),
            'title': doc.metadata.get('title', 'Unknown'),
            'author': doc.metadata.get('author'),
            'chapter': doc.metadata.get('chapter'),
        }
        for doc in docs
    ]


def load_vector_db(
    embedding: Embeddings, table_name: str = 'hr_information', query_name: str = 'match_documents'
) -> SupabaseVectorStore:
    """
    Initializes a SupabaseVectorStore with the given embedding model and configuration.

    Parameters:
        embedding (Embeddings): The embedding model to use for vector operations.
        table_name (str): The name of the Supabase table used for storing vectors.
        query_name (str): The name of the stored procedure or query for similarity search
                          (default is 'match_documents').

    Returns:
        SupabaseVectorStore: A vector store instance connected to the specified Supabase table.
    """
    return SupabaseVectorStore(
        client=get_supabase_client(),
        embedding=embedding,
        table_name=table_name,
        query_name=query_name,
    )


def load_authors_licenses_mapping(
    file_path: Path = Path(__file__).parent / 'document-authors-licenses.json',
) -> dict:
    """
    Loads a mapping from document filename to author name and license from a JSON file.
    """
    with open(file_path) as f:
        return json.load(f)
