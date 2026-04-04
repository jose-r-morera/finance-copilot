import structlog
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = structlog.get_logger(__name__)


class DocumentProcessor:
    """
    Service to split large documents into manageable chunks for vector storage.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    def process_sections(self, sections: dict[str, str], metadata: dict) -> list[dict]:
        """
        Processes a dictionary of sections into a list of chunks with metadata.
        """
        all_chunks = []
        for section_name, content in sections.items():
            if not content:
                continue

            logger.info("Chunking section", section=section_name, length=len(content))
            chunks = self.splitter.split_text(content)

            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata.update(
                    {"section": section_name, "chunk_index": i, "total_chunks": len(chunks)}
                )
                all_chunks.append({"content": chunk, "metadata": chunk_metadata})

        logger.info("Finished document processing", total_chunks=len(all_chunks))
        return all_chunks


document_processor = DocumentProcessor()
