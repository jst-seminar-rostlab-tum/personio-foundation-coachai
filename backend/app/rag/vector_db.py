import json
import os
import re
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


def is_reference_page(text: str) -> bool:
    """
    Determines if an entire page is primarily references/TOC/index.
    Should be called BEFORE cleaning to catch reference-heavy pages.
    """
    if not text or len(text.strip()) < 50:
        return False

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return False

    # Count how many lines look like references/TOC
    reference_line_count = 0

    for line in lines:
        # TOC patterns: "10.3.1: Pre-interview Preparation 528"
        if re.match(r'^\d+(\.\d+)*[:.]?\s+[A-Z]', line):
            reference_line_count += 1
            continue

        # URLs (with or without text)
        if re.search(r'https?://|www\.[\w\-.]+\.[a-z]{2,}', line, re.IGNORECASE):
            reference_line_count += 1
            continue

        # Citation patterns
        citation_patterns = [
            r'Retrieved from',
            r'Available at:?',
            r'accessed\s+(on\s+)?(January|February|March|April|May|June|July|August|September|October|November'
            r'|December)',
            r'doi:\s*10\.',
            r'\(\d{4}\)[\.\,]',  # (2024).
            r'et al[\.,]',
            r'^\[?\d+\]',  # [1] or 1.
        ]

        if any(re.search(pattern, line, re.IGNORECASE) for pattern in citation_patterns):
            reference_line_count += 1
            continue

    # If more than 60% of lines are references/TOC, consider it a reference page
    reference_ratio = reference_line_count / len(lines)
    return reference_ratio > 0.6


def remove_citations_and_captions(text: str) -> str:
    """
    Removes citations and captions from text while preserving the main content.
    Enhanced with better URL and TOC detection.
    """
    if not text:
        return text

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line_stripped = line.strip()

        if not line_stripped:
            cleaned_lines.append(line)
            continue

        if re.search(r'^\d+[).]\s*\n?', line_stripped):
            continue

        # Skip TOC entries: "10.3.1: Pre-interview Preparation 528"
        if re.match(r'^\d+(\.\d+)*[:.]?\s+[A-Z][\w\s]+(\d+)?$', line_stripped):
            continue

        # Remove image/figure/table captions
        if re.match(
            r'^(Image|Figure|Table|Chart|Diagram)\s*[:.]?\s*', line_stripped, re.IGNORECASE
        ):
            continue

        # Enhanced citation indicators
        citation_indicators = [
            r'Retrieved from',
            r'Available at:?',
            r'accessed\s+(on\s+)?(January|February|March|April|May|June|July|August|September|October|November'
            r'|December)',
            r'^\s*\[?\d+\]?\s*[\w\s,&\.]+\(\d{4}[,)]',
            r'doi:\s*10\.',
            r'^https?://',
            r'^www\.[\w\-\.]+',  # Lines starting with www.
            r'^\(https?://',  # (http://...
        ]

        is_citation = False
        for pattern in citation_indicators:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                is_citation = True
                break

        if is_citation:
            continue

        # Clean inline citations
        line_cleaned = re.sub(
            r'\b[\w\s,&.]+\.\s*\(\d{4}[^)]*\)\.\s*[^\n]*\.\s*\[[^]]+]\.', '', line_stripped
        )

        # Remove URLs more aggressively
        line_cleaned = re.sub(r'https?://\S+', '', line_cleaned)
        line_cleaned = re.sub(r'www\.[\w\-.]+\.[a-z]{2,}\S*', '', line_cleaned, flags=re.IGNORECASE)

        # Remove citation patterns
        line_cleaned = re.sub(r'\([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,?\s+\d{4}\)', '', line_cleaned)
        line_cleaned = re.sub(r'\[\d+]', '', line_cleaned)

        # Remove "accessed [date]" patterns
        line_cleaned = re.sub(
            r'\(accessed\s+(on\s+)?\w+\s+\d+,?\s+\d{4}\)', '', line_cleaned, flags=re.IGNORECASE
        )

        # Clean up extra spaces
        line_cleaned = re.sub(r'\s+', ' ', line_cleaned).strip()

        # Only add if there's meaningful content
        if line_cleaned and len(line_cleaned) > 10:
            cleaned_lines.append(line_cleaned)

    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def should_exclude_chunk(doc: Document) -> bool:
    """
    Determines if a text chunk should be excluded from the vector database.
    Enhanced to catch more edge cases.
    """
    text = doc.page_content
    if not text or len(text.strip()) < 30:
        return True

    text_stripped = text.strip()
    word_count = len(text_stripped.split())

    # Exclude very short chunks
    if word_count < 5:
        return True

    # Check if it's a TOC fragment that slipped through
    # "10.3.1: Pre-interview Preparation"
    if re.match(r'^\d+(\.\d+)+[:.]?\s+[A-Z]', text_stripped):
        return True

    # Exclude if it's mostly numbers and colons (TOC page numbers)
    number_colon_ratio = len(re.findall(r'[\d:.]', text_stripped)) / len(text_stripped)
    if number_colon_ratio > 0.4:
        return True

    # Exclude if it contains URLs or www
    if re.search(r'https?://|www\.[\w\-.]+', text_stripped, re.IGNORECASE):
        return True

    # Exclude if it has "accessed [date]" pattern
    if re.search(r'accessed\s+\w+\s+\d+,?\s+\d{4}', text_stripped, re.IGNORECASE):
        return True

    # Existing checks - ADDED 'contents' to the list
    reference_indicators = [
        'references',
        'bibliography',
        'works cited',
        'further reading',
        'contents',
    ]
    if any(text_stripped.lower() == ind for ind in reference_indicators):
        return True

    if 'chatgpt' in text_stripped.lower():
        return True

    chapter = doc.metadata.get('chapter', '')
    return chapter and any(
        term in chapter.strip().lower()
        for term in [
            'references',
            'bibliography',
            'works cited',
            'version history',
            'detailed licensing',
            'index',
            'further reading',
            'errata',
            'image credits',
            'survey',
            'resources',
            'contents',
            'discussion questions',
        ]
    )


def extract_toc(file_path: str) -> tuple[list, int]:
    """
    Extracts TOC by analyzing text layout and positions
    """
    with pymupdf.open(file_path) as doc:
        total_pages = len(doc)
        toc = doc.get_toc(simple=True)
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
    Enhanced with page-level filtering before splitting.
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

                filtered_loaded_docs = []
                for doc in loaded_docs:
                    # FIRST: Check if entire page is references/TOC before cleaning
                    if is_reference_page(doc.page_content):
                        print(f'  ⏭️  Skipping reference/TOC page {doc.metadata.get("page", "?")}')
                        continue

                    # THEN: Clean the content
                    doc.page_content = doc.page_content.replace('\u0000', '')
                    doc.page_content = remove_citations_and_captions(doc.page_content)

                    # Skip if cleaning removed everything
                    if not doc.page_content or len(doc.page_content.strip()) < 30:
                        continue

                    doc.metadata['licenseName'] = license_name
                    doc.metadata['author'] = author
                    doc.metadata['chapter'] = page_chapter_map.get(doc.metadata.get('page', 0))
                    doc.metadata.pop('source', None)

                    filtered_loaded_docs.append(doc)

                splits = text_splitter.split_documents(filtered_loaded_docs)
                filtered_splits = [split for split in splits if not should_exclude_chunk(split)]
                docs.extend(filtered_splits)
                print(f'✅ Successfully processed {file} with {len(filtered_splits)} chunks')
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
