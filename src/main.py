"""Main application entry point for Document Data Extractor."""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.configuration_manager import ConfigurationManager
from ui.main_window import MainWindow
from controllers.app_controller import AppController


def main():
    """Initialize and run the application."""
    try:
        # Load configuration
        print("Loading configuration...")
        config_manager = ConfigurationManager()

        # Create application controller
        print("Initializing application controller...")
        app_controller = AppController(config_manager)
        
        print(f"Output folder: {app_controller.config.output_folder}")
        print(f"Log directory: {app_controller.config.log_directory}")
        
        # Create main window (use app_controller's config so they share the same object)
        print("Creating main window...")
        main_window = MainWindow(app_controller.config)
        
        # Set up controller callbacks for UI updates
        app_controller.set_ui_update_callback(main_window.update_state)
        app_controller.set_error_callback(main_window.show_error)
        app_controller.set_success_callback(main_window.show_success)
        app_controller.set_poll_callback(main_window.after)

        # Register all callbacks
        print("Registering event handlers...")

        # File selection (multi-file support)
        main_window.on_file_selected(app_controller.on_files_selected)

        # Keyword management
        main_window.on_keyword_added(app_controller.on_keyword_added)
        main_window.on_keyword_selected_from_history(
            app_controller.on_keyword_selected_from_history
        )
        main_window.on_keyword_removed(app_controller.on_keyword_removed)
        main_window.on_keywords_cleared(app_controller.on_keywords_cleared)
        
        # Preset management
        main_window.on_preset_create(app_controller.on_preset_created)
        main_window.on_preset_load(app_controller.on_preset_loaded)
        main_window.on_preset_edit(app_controller.on_preset_updated)
        main_window.on_preset_delete(app_controller.on_preset_deleted)
        main_window.on_presets_section_toggled(app_controller.on_presets_section_toggled)

        # Extraction
        main_window.on_extract_clicked(app_controller.on_extract_clicked)

        # Settings
        main_window.on_settings_changed(app_controller.on_settings_changed)

        # Results actions
        main_window.on_open_output_file(app_controller.on_open_output_file)
        main_window.on_open_output_folder(app_controller.on_open_output_folder)
        main_window.on_open_log_file(app_controller.on_open_log_file)

        # Start application
        print("Starting application...")
        print("-" * 50)
        main_window.show()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
