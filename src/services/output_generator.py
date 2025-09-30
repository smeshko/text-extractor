"""Output generator for creating plain text extraction reports."""

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.extraction_results import ExtractionResults
from models.configuration import Configuration


class OutputResult:
    """Result of output generation.

    Attributes:
        success: Whether generation succeeded
        output_path: Path to generated output file (if successful)
        error_message: Error description if generation failed
    """

    def __init__(self, success: bool, output_path: str | None = None,
                 error_message: str | None = None):
        self.success = success
        self.output_path = output_path
        self.error_message = error_message


class OutputGenerator:
    """Generates plain text output files from extraction results.

    Output format:
    - UTF-8 encoding
    - Windows line endings (\\r\\n)
    - Human-readable plain text
    - Sections: Document info, Personal info, Keyword extractions, Summary, Warnings, Errors
    """

    def generate(self, results: ExtractionResults, config: Configuration) -> OutputResult:
        """Generate output file from extraction results.

        Args:
            results: ExtractionResults from extraction engine
            config: Configuration with output folder path

        Returns:
            OutputResult with file path and status
        """
        try:
            # Validate output folder is writable
            if not os.access(config.output_folder, os.W_OK):
                return OutputResult(
                    success=False,
                    error_message=f"Output folder is not writable: {config.output_folder}"
                )

            # Generate filename
            output_filename = self.generate_filename(results.document.filename)
            output_path = os.path.join(config.output_folder, output_filename)

            # Handle file collision
            if os.path.exists(output_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = output_filename.rsplit('.', 1)[0]
                output_filename = f"{base_name}_{timestamp}.txt"
                output_path = os.path.join(config.output_folder, output_filename)

            # Format output content
            content = self.format_output(results)

            # Write to file with UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(content)

            return OutputResult(
                success=True,
                output_path=output_path
            )

        except OSError as e:
            return OutputResult(
                success=False,
                error_message=f"Insufficient disk space or I/O error: {str(e)}"
            )
        except Exception as e:
            return OutputResult(
                success=False,
                error_message=f"Failed to generate output: {str(e)}"
            )

    def format_output(self, results: ExtractionResults) -> str:
        """Format extraction results as plain text.

        Args:
            results: ExtractionResults to format

        Returns:
            Formatted plain text string (UTF-8)
        """
        lines = []

        # Document metadata
        lines.append(f"Document: {results.document.filename}")
        lines.append(f"Processed: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Personal Information section
        lines.append("--- Personal Information ---")
        if results.personal_info.first_name:
            lines.append(f"First Name: {results.personal_info.first_name}")
        else:
            lines.append("First Name: Not found")

        if results.personal_info.last_name:
            lines.append(f"Last Name: {results.personal_info.last_name}")
        else:
            lines.append("Last Name: Not found")

        if results.personal_info.id_number_prefix:
            lines.append(f"ID Number: {results.personal_info.id_number_prefix}***")
        else:
            lines.append("ID Number: Not found")

        if results.personal_info.character_set != 'unknown':
            lines.append(f"Character Set: {results.personal_info.character_set.capitalize()}")

        lines.append("")

        # Keyword Extractions section
        lines.append("--- Keyword Extractions ---")

        if results.matches:
            # Group matches by keyword
            keyword_groups = {}
            for match in results.matches:
                if match.keyword not in keyword_groups:
                    keyword_groups[match.keyword] = []
                keyword_groups[match.keyword].append(match)

            # Output each keyword's matches
            for keyword, matches in keyword_groups.items():
                for match in matches:
                    if match.status == 'found':
                        if match.line_number is not None:
                            lines.append(
                                f"{match.keyword}: {match.value} "
                                f"(Page {match.page_number}, Line {match.line_number})"
                            )
                        else:
                            lines.append(
                                f"{match.keyword}: {match.value} "
                                f"(Page {match.page_number})"
                            )
                    elif match.status == 'not_found':
                        lines.append(f"{match.keyword}: Not found")
                    elif match.status == 'ambiguous':
                        if match.line_number is not None:
                            lines.append(
                                f"{match.keyword}: {match.value} "
                                f"(Page {match.page_number}, Line {match.line_number}) "
                                f"[Ambiguous]"
                            )
                        else:
                            lines.append(
                                f"{match.keyword}: {match.value} "
                                f"(Page {match.page_number}) [Ambiguous]"
                            )
        else:
            lines.append("No keyword extractions performed")

        lines.append("")

        # Processing Summary
        lines.append("--- Processing Summary ---")

        # Get unique keywords
        unique_keywords = set(m.keyword for m in results.matches)
        if unique_keywords:
            lines.append(f"Total keywords: {len(unique_keywords)} ({', '.join(sorted(unique_keywords))})")
        else:
            lines.append("Total keywords: 0")

        lines.append(f"Successful extractions: {results.get_success_count()}")
        lines.append(f"Not found: {results.get_not_found_count()}")

        if results.get_ambiguous_count() > 0:
            lines.append(f"Ambiguous: {results.get_ambiguous_count()}")

        lines.append(f"Processing time: {results.processing_time:.2f} seconds")
        lines.append("")

        # Warnings section
        lines.append("--- Warnings ---")
        if results.has_warnings():
            for warning in results.warnings:
                lines.append(f"- {warning}")
        else:
            lines.append("None")
        lines.append("")

        # Errors section
        lines.append("--- Errors ---")
        if results.has_errors():
            for error in results.errors:
                lines.append(f"- {error['message']}")
        else:
            lines.append("None")

        return '\n'.join(lines)

    def generate_filename(self, document_filename: str) -> str:
        """Generate output filename from document filename.

        Args:
            document_filename: Original document filename

        Returns:
            Output filename: 'output_[original_filename].txt'
        """
        # Remove extension if present
        if '.' in document_filename:
            base_name = document_filename.rsplit('.', 1)[0]
        else:
            base_name = document_filename

        return f"output_{base_name}.txt"
