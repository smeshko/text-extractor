"""AppController - Main application controller coordinating UI and business logic."""

import sys
import os
from pathlib import Path
from typing import Callable, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.document import Document
from models.keyword import Keyword
from models.configuration import Configuration
from models.application_state import ApplicationState, ProcessingStatus
from controllers.state_manager import StateManager
from controllers.thread_coordinator import ThreadCoordinator, ProgressReporter
from parsers.factory import ParserFactory
from extractors.extraction_engine import ExtractionEngine
from services.output_generator import OutputGenerator
from services.processing_logger import ProcessingLogger
from services.configuration_manager import ConfigurationManager


class AppController:
    """Application controller coordinating UI and business logic.

    Responsibilities:
    - Handle user actions from UI
    - Coordinate business logic execution
    - Manage application state
    - Update UI based on state changes
    """

    def __init__(self, config_manager: ConfigurationManager):
        """Initialize application controller.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.load()

        # State management
        self.state_manager = StateManager()
        self.thread_coordinator = ThreadCoordinator()
        
        # Services
        self.output_generator = OutputGenerator()
        self.logger: Optional[ProcessingLogger] = None
        
        # UI callbacks
        self._ui_update_callback: Optional[Callable[[ApplicationState], None]] = None
        self._error_callback: Optional[Callable[[str], None]] = None
        self._success_callback: Optional[Callable[[str], None]] = None
        self._poll_callback: Optional[Callable[[int, Callable], None]] = None
        
        # Register state change observer
        self.state_manager.add_observer(self._on_state_changed)

    def set_ui_update_callback(self, callback: Callable[[ApplicationState], None]) -> None:
        """Set callback for UI updates.
        
        Args:
            callback: Function(state: ApplicationState) -> None
        """
        self._ui_update_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for error messages.
        
        Args:
            callback: Function(error_message: str) -> None
        """
        self._error_callback = callback
    
    def set_success_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for success messages.
        
        Args:
            callback: Function(success_message: str) -> None
        """
        self._success_callback = callback
    
    def set_poll_callback(self, callback: Callable[[int, Callable], None]) -> None:
        """Set callback for scheduling polling.
        
        Args:
            callback: Function(milliseconds: int, func: Callable) -> None
        """
        self._poll_callback = callback
    
    def on_file_selected(self, file_path: str) -> None:
        """Handle file selection.
        
        Args:
            file_path: Path to selected file
        """
        print(f"DEBUG AppController.on_file_selected called with: {file_path}")
        try:
            # Create document from file path
            print(f"DEBUG: Creating Document.from_path...")
            document = Document.from_path(file_path)
            print(f"DEBUG: Document created: {document.filename}")
            
            # Validate file exists
            if not document.validate_exists():
                self._show_error(f"File not found: {file_path}")
                return

            # Validate file is readable
            if not document.validate_readable():
                self._show_error(f"File is not readable: {file_path}")
                return

            # Validate file size
            if not document.validate_size(max_size_mb=50):
                self._show_error(f"File is too large (max 50MB): {file_path}")
                return
            
            # Validate document using parser
            parser = ParserFactory.create(file_path)
            validation_result = parser.validate(file_path)

            if not validation_result.is_valid:
                document.mark_invalid(validation_result.error_message or "Unknown error")
                self._show_error(validation_result.error_message or "Invalid document")
                return

            # Get page count
            try:
                page_count = parser.get_page_count(file_path)
                document.mark_valid(page_count)
            except Exception as e:
                document.mark_invalid(f"Failed to get page count: {e}")
                self._show_error(f"Failed to validate document: {e}")
                return

            # Update state
            self.state_manager.set_document(document)
            print(f"DEBUG: Document set: {document.filename}")

        except Exception as e:
            self._show_error(f"Error selecting file: {e}")
            import traceback
            traceback.print_exc()
    
    def on_keyword_added(self, keyword_text: str) -> None:
        """Handle keyword addition.

        Args:
            keyword_text: Keyword text to add
        """
        try:
            # Validate keyword text
            keyword_text = keyword_text.strip()
            if not keyword_text:
                self._show_error("Keyword cannot be empty")
                return
            
            if len(keyword_text) > 100:
                self._show_error("Keyword must be 1-100 characters")
                return
            
            # Create keyword
            keyword = Keyword.from_text(keyword_text, is_historical=False)
            
            # Check for duplicates
            state = self.state_manager.get_state()
            if any(kw.matches(keyword) for kw in state.active_keywords):
                self._show_error(f"Keyword '{keyword_text}' already added")
                return
            
            # Add keyword to state
            self.state_manager.add_keyword(keyword)
            print(f"DEBUG: Keyword added: {keyword_text}")

            # Add to history and save config (check for duplicates)
            keyword_lower = keyword_text.lower()
            if not any(kw.lower() == keyword_lower for kw in self.config.keyword_history):
                self.config.keyword_history.append(keyword_text)
                self.config_manager.save(self.config)
            
        except Exception as e:
            self._show_error(f"Error adding keyword: {e}")
            import traceback
            traceback.print_exc()
    
    def on_keyword_removed(self, keyword_text: str) -> None:
        """Handle keyword removal.

        Args:
            keyword_text: Keyword text to remove
        """
        try:
            self.state_manager.remove_keyword(keyword_text)
        except Exception as e:
            self._show_error(f"Error removing keyword: {e}")
    
    def on_keywords_cleared(self) -> None:
        """Handle clearing all keywords."""
        try:
            self.state_manager.clear_keywords()
        except Exception as e:
            self._show_error(f"Error clearing keywords: {e}")
    
    def on_keyword_selected_from_history(self, keyword_text: str) -> None:
        """Handle keyword selection from history.

        Args:
            keyword_text: Keyword text from history
        """
        try:
            # Create keyword from history
            keyword = Keyword.from_text(keyword_text, is_historical=True)
            
            # Check for duplicates
            state = self.state_manager.get_state()
            if any(kw.matches(keyword) for kw in state.active_keywords):
                self._show_error(f"Keyword '{keyword_text}' already added")
                return
            
            # Add keyword to state
            self.state_manager.add_keyword(keyword)
            
        except Exception as e:
            self._show_error(f"Error selecting keyword from history: {e}")
    
    def on_preset_created(self, name: str, keywords: list[str]) -> None:
        """Handle preset creation.
        
        Args:
            name: Preset name
            keywords: List of keywords
        """
        try:
            success, error = self.config.add_preset(name, keywords)
            if success:
                self.config_manager.save(self.config)
                # Refresh KeywordPanel presets (handled by main_window)
            else:
                self._show_error(error)
        except Exception as e:
            self._show_error(f"Error creating preset: {e}")
    
    def on_preset_loaded(self, preset_name: str) -> None:
        """Handle preset loading.
        
        Args:
            preset_name: Name of preset to load
        """
        try:
            print(f"DEBUG: Loading preset '{preset_name}'")
            preset = self.config.get_preset_by_name(preset_name)
            if preset:
                print(f"DEBUG: Found preset with {len(preset['keywords'])} keywords: {preset['keywords']}")
                # Clear existing keywords
                self.state_manager.clear_keywords()
                print(f"DEBUG: Cleared keywords")
                
                # Add preset keywords
                for keyword_text in preset['keywords']:
                    keyword = Keyword.from_text(keyword_text, is_historical=False)
                    self.state_manager.add_keyword(keyword)
                    print(f"DEBUG: Added keyword '{keyword_text}'")
                
                print(f"DEBUG: Final state has {len(self.state_manager.get_state().active_keywords)} keywords")
            else:
                self._show_error(f"Preset '{preset_name}' not found")
        except Exception as e:
            self._show_error(f"Error loading preset: {e}")
            import traceback
            traceback.print_exc()
    
    def on_preset_updated(self, old_name: str, new_name: str, keywords: list[str]) -> None:
        """Handle preset update.
        
        Args:
            old_name: Current preset name
            new_name: New preset name
            keywords: Updated keyword list
        """
        try:
            success, error = self.config.update_preset(old_name, new_name, keywords)
            if success:
                self.config_manager.save(self.config)
                # Refresh KeywordPanel presets (handled by main_window)
            else:
                self._show_error(error)
        except Exception as e:
            self._show_error(f"Error updating preset: {e}")
    
    def on_preset_deleted(self, name: str) -> None:
        """Handle preset deletion.
        
        Args:
            name: Preset name
        """
        try:
            if self.config.delete_preset(name):
                self.config_manager.save(self.config)
                # Refresh KeywordPanel presets (handled by main_window)
            else:
                self._show_error(f"Preset '{name}' not found")
        except Exception as e:
            self._show_error(f"Error deleting preset: {e}")
    
    def on_presets_section_toggled(self, expanded: bool) -> None:
        """Handle presets section toggle.
        
        Args:
            expanded: True if expanded, False if collapsed
        """
        try:
            self.config.presets_section_expanded = expanded
            self.config_manager.save(self.config)
        except Exception as e:
            self._show_error(f"Error saving preset section state: {e}")
    
    def on_extract_clicked(self) -> None:
        """Handle extract button click."""
        print("DEBUG: Extract button clicked!")
        try:
            # Check if extraction can start
            state = self.state_manager.get_state()
            print(f"DEBUG: State - doc: {state.current_document}, keywords: {len(state.active_keywords)}, can_extract: {self.state_manager.can_start_extraction()}")
            
            if not self.state_manager.can_start_extraction():
                self._show_error("Cannot start extraction. Please select a file and add keywords.")
                return

            # Get current state
            state = self.state_manager.get_state()

            # Start processing
            if not self.state_manager.start_processing():
                self._show_error("Failed to start extraction")
                return

            # Initialize logger
            self.logger = ProcessingLogger(self.config.log_directory)
            keywords_text = [kw.text for kw in state.active_keywords]
            self.logger.start_logging(state.current_document.filename, keywords_text)

            # Start extraction in background thread
            self.thread_coordinator.start_extraction(
                self._perform_extraction,
                state.current_document,
                state.active_keywords
            )
            
            # Start polling for messages
            self._poll_worker_messages()
            
        except Exception as e:
            self.state_manager.fail_processing(str(e))
            self._show_error(f"Error starting extraction: {e}")
    
    def on_settings_changed(self, new_config: Configuration) -> None:
        """Handle settings change.
        
        Args:
            new_config: Updated configuration
        """
        try:
            # Validate configuration
            is_valid, errors = self.config_manager.validate(new_config)
            if not is_valid:
                self._show_error(f"Invalid settings: {', '.join(errors)}")
                return
            
            # Save configuration
            if self.config_manager.save(new_config):
                self.config = new_config
                self._show_success("Settings saved successfully")
            else:
                self._show_error("Failed to save settings")
                
        except Exception as e:
            self._show_error(f"Error saving settings: {e}")
    
    def on_output_folder_changed(self, folder_path: str) -> None:
        """Handle output folder change.
        
        Args:
            folder_path: New output folder path
        """
        try:
            # Validate folder
            path = Path(folder_path)
            if not path.exists():
                # Try to create
                path.mkdir(parents=True, exist_ok=True)
            
            if not path.is_dir():
                self._show_error(f"Not a valid directory: {folder_path}")
                return
            
            # Update config
            self.config.output_folder = folder_path
            self.config_manager.save(self.config)
            
        except Exception as e:
            self._show_error(f"Error changing output folder: {e}")
    
    def on_log_directory_changed(self, directory_path: str) -> None:
        """Handle log directory change.
        
        Args:
            directory_path: New log directory path
        """
        try:
            # Validate directory
            path = Path(directory_path)
            if not path.exists():
                # Try to create
                path.mkdir(parents=True, exist_ok=True)
            
            if not path.is_dir():
                self._show_error(f"Not a valid directory: {directory_path}")
                return
            
            # Update config
            self.config.log_directory = directory_path
            self.config_manager.save(self.config)
            
        except Exception as e:
            self._show_error(f"Error changing log directory: {e}")
    
    def _perform_extraction(self, document: Document, keywords: list[Keyword]):
        """Perform extraction in worker thread.

        Args:
            document: Document to process
            keywords: Keywords to extract

        Returns:
            ExtractionResults
        """
        # Create progress reporter
        reporter = ProgressReporter(self.thread_coordinator)
        
        try:
            # Log start
            if self.logger:
                self.logger.log_event('INFO', f'Starting extraction: {document.filename}')
            
            reporter.report('Parsing document...')
            
            # Parse document
            parser = ParserFactory.create(document.file_path)
            parse_result = parser.parse(document.file_path)

            if not parse_result.success:
                raise Exception(parse_result.error_message or "Failed to parse document")

            if self.logger:
                self.logger.log_event('INFO', f'Document parsed successfully: {len(parse_result.pages)} pages')
            
            reporter.report('Extracting data...')

            # Extract data
            extraction_engine = ExtractionEngine()
            keyword_texts = [kw.text for kw in keywords]
            results = extraction_engine.extract(parse_result.pages, keyword_texts, document)
            
            if self.logger:
                self.logger.log_event('INFO', f'Extraction complete: {len(results.matches)} matches')
            
            reporter.report('Generating output...')
            
            # Generate output file
            output_result = self.output_generator.generate(results, self.config)

            if not output_result.success:
                raise Exception(output_result.error_message or "Failed to generate output")

            results.output_path = output_result.output_path

            # Save log path before finalizing
            if self.logger:
                results.log_path = self.logger.get_log_path()
                self.logger.log_event('INFO', f'Output written to: {output_result.output_path}')
                self.logger.finalize('success', results)

            reporter.report('Complete!')

            return results

        except Exception as e:
            if self.logger:
                self.logger.log_event('ERROR', f'Extraction failed: {e}')
                self.logger.finalize('failure', None)
            raise

    def _poll_worker_messages(self) -> None:
        """Poll for messages from worker thread."""
        # Check for messages
        messages = self.thread_coordinator.check_messages()

        for msg in messages:
            msg_type = msg.get('type')

            if msg_type == 'progress':
                # Update progress message (could notify UI)
                pass

            elif msg_type == 'complete':
                # Extraction complete
                results = msg.get('results')
                self.state_manager.complete_processing(results)
                # Note: UI update happens via state change notification
                # which calls results_display.show_results() with full paths

            elif msg_type == 'error':
                # Extraction error
                error_message = msg.get('message', 'Unknown error')
                self.state_manager.fail_processing(error_message)
                self._show_error(f"Extraction failed: {error_message}")
        
        # Continue polling if still running
        if self.thread_coordinator.is_running():
            # Schedule next poll in 100ms using UI callback
            if self._poll_callback:
                self._poll_callback(100, self._poll_worker_messages)
    
    def get_worker_messages(self) -> list[dict]:
        """Get messages from worker thread (for UI polling).
        
        Returns:
            List of messages from worker thread
        """
        return self.thread_coordinator.check_messages()
    
    def _on_state_changed(self, state: ApplicationState) -> None:
        """Handle state change notification.
        
        Args:
            state: New application state
        """
        print(f"DEBUG AppController: _on_state_changed called with {len(state.active_keywords)} keywords")
        print(f"DEBUG AppController: UI callback registered: {self._ui_update_callback is not None}")
        # Notify UI
        if self._ui_update_callback:
            self._ui_update_callback(state)
        else:
            print(f"DEBUG AppController: ERROR - No UI update callback registered!")
    
    def _show_error(self, message: str) -> None:
        """Show error message to user.
        
        Args:
            message: Error message
        """
        if self._error_callback:
            self._error_callback(message)
    
    def _show_success(self, message: str) -> None:
        """Show success message to user.
        
        Args:
            message: Success message
        """
        if self._success_callback:
            self._success_callback(message)
    
    def get_config(self) -> Configuration:
        """Get current configuration.
        
        Returns:
            Current configuration
        """
        return self.config
    
    def get_state(self) -> ApplicationState:
        """Get current application state.
        
        Returns:
            Current application state
        """
        return self.state_manager.get_state()
    
    def on_open_output_file(self) -> None:
        """Handle open output file action."""
        try:
            state = self.state_manager.get_state()
            if state.extraction_results and hasattr(state.extraction_results, 'output_path'):
                output_path = state.extraction_results.output_path
                if output_path and Path(output_path).exists():
                    # Open file with default application
                    import subprocess
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', output_path])
                    elif sys.platform == 'win32':  # Windows
                        os.startfile(output_path)
                    else:  # Linux
                        subprocess.run(['xdg-open', output_path])
                else:
                    self._show_error("Output file not found")
            else:
                self._show_error("No output file available")
        except Exception as e:
            self._show_error(f"Error opening output file: {e}")
    
    def on_open_output_folder(self) -> None:
        """Handle open output folder action."""
        try:
            output_folder = self.config.output_folder
            if Path(output_folder).exists():
                # Open folder with default file manager
                import subprocess
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', output_folder])
                elif sys.platform == 'win32':  # Windows
                    os.startfile(output_folder)
                else:  # Linux
                    subprocess.run(['xdg-open', output_folder])
            else:
                self._show_error(f"Output folder not found: {output_folder}")
        except Exception as e:
            self._show_error(f"Error opening output folder: {e}")
    
    def on_open_log_file(self) -> None:
        """Handle open log file action."""
        try:
            if self.logger and hasattr(self.logger, 'log_path'):
                log_path = self.logger.log_path
                if log_path and Path(log_path).exists():
                    # Open file with default application
                    import subprocess
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', log_path])
                    elif sys.platform == 'win32':  # Windows
                        os.startfile(log_path)
                    else:  # Linux
                        subprocess.run(['xdg-open', log_path])
                else:
                    self._show_error("Log file not found")
            else:
                self._show_error("No log file available")
        except Exception as e:
            self._show_error(f"Error opening log file: {e}")