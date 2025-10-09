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

    def _calculate_column_widths(self, headers: list[str], rows: list[list[str]]) -> list[int]:
        """Calculate optimal column widths for table formatting.

        Args:
            headers: Column headers
            rows: Data rows (each row is list of cell values)

        Returns:
            List of column widths (max of header and all values per column)
        """
        if not headers:
            return []

        # Start with header widths
        widths = [len(header) for header in headers]

        # Update with max value width per column
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

        return widths

    def _format_table_row(self, cells: list[str], widths: list[int]) -> str:
        """Format a single table row with column alignment.

        Args:
            cells: Cell values for this row
            widths: Column widths for alignment

        Returns:
            Formatted row string with left-aligned cells
        """
        formatted_cells = []
        for i, cell in enumerate(cells):
            if i < len(widths):
                # Left-align with padding (minimum 4 spaces between columns)
                formatted_cells.append(str(cell).ljust(widths[i] + 4))
            else:
                formatted_cells.append(str(cell))

        return ''.join(formatted_cells).rstrip()

    def _add_semicolon_if_numeric(self, value: str) -> str:
        """Add semicolon suffix to numeric values.

        Args:
            value: Value to check and potentially suffix

        Returns:
            Value with semicolon if numeric, unchanged otherwise

        Example:
            "1234" → "1234;"
            "3,5" → "3,5;"
            "Not found" → "Not found"
        """
        if not value:
            return value

        # Check if value is numeric (allowing commas and decimals)
        # Remove commas and check if it's a valid number
        cleaned = value.replace(',', '.').strip()
        try:
            float(cleaned)
            return f"{value};"
        except ValueError:
            # Not numeric, return as-is
            return value

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

            # Generate filename from personal information
            output_filename = self.generate_filename(results.personal_info)
            output_path = os.path.join(config.output_folder, output_filename)

            # Note: No file collision handling per FR-009 - files will be overwritten

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

        # Use table format if we have full_name and age
        if results.personal_info.full_name and results.personal_info.age:
            abbrev_name = results.personal_info.get_abbreviated_name() or "???"
            # Add semicolon after abbreviated name
            abbrev_name_with_semi = f"{abbrev_name};"
            headers = ["ИМЕ", "ГОДИНИ"]
            rows = [[abbrev_name_with_semi, str(results.personal_info.age)]]
            widths = self._calculate_column_widths(headers, rows)

            lines.append(self._format_table_row(headers, widths))
            lines.append(self._format_table_row(rows[0], widths))
        else:
            # Fallback to legacy format if missing personal info
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

            # Build table: headers are keywords, rows contain values
            headers = sorted(keyword_groups.keys())

            # Collect all values for each keyword (support multiple matches per keyword)
            max_matches = max(len(matches) for matches in keyword_groups.values())
            rows = []

            for row_idx in range(max_matches):
                row = []
                for keyword in headers:
                    matches = keyword_groups[keyword]
                    if row_idx < len(matches):
                        match = matches[row_idx]
                        if match.status == 'found':
                            # Add semicolon for numeric values
                            value = self._add_semicolon_if_numeric(match.value)
                            row.append(value)
                        elif match.status == 'not_found':
                            row.append("Not found")
                        elif match.status == 'ambiguous':
                            # Add semicolon for numeric values, plus [Ambiguous] marker
                            value = self._add_semicolon_if_numeric(match.value)
                            row.append(f"{value} [Ambiguous]")
                    else:
                        row.append("")  # Empty cell if this keyword has fewer matches
                rows.append(row)

            # Format table
            widths = self._calculate_column_widths(headers, rows)
            lines.append(self._format_table_row(headers, widths))
            for row in rows:
                lines.append(self._format_table_row(row, widths))
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

    def generate_filename(self, personal_info) -> str:
        """Generate output filename from personal information.

        Args:
            personal_info: PersonalInformation with full_name and age

        Returns:
            Filename in format "{ABBREV}-{AGE}.txt" (e.g., "ИЙТ-33.txt")
            Falls back to timestamp format if personal info incomplete

        Examples:
            full_name="Иван Йорданов Тодоров", age=33 → "ИЙТ-33.txt"
            full_name="John Doe", age=25 → "JD-25.txt"
            full_name=None → "output_20251009_143022.txt"
        """
        # Try to generate abbreviated name-based filename
        if personal_info.full_name and personal_info.age:
            abbrev_name = personal_info.get_abbreviated_name()
            if abbrev_name:
                return f"{abbrev_name}-{personal_info.age}.txt"

        # Fallback to timestamp format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"output_{timestamp}.txt"
