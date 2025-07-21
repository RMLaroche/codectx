"""
Interactive mode implementation for codectx
"""
from typing import Dict, Any, List
from rich.console import Console
from rich.progress import Progress
from rich.live import Live
from InquirerPy import inquirer

from ..core.discovery import discover_files
from ..core.processor import FileProcessor
from ..core.summary_parser import SummaryParser
from ..core.models import ProcessingConfig, ProcessingMode, FileInfo, ProcessingResult
from ..ui.components import (
    display_welcome_banner,
    create_file_table,
    create_discovery_summary_panel,
    create_live_processing_layout,
    display_processing_complete,
    display_error,
    display_info
)
from ..utils.utils import get_timestamp


class InteractiveMode:
    """Interactive mode for user-friendly file processing"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def run(self, directory_path: str = ".") -> None:
        """
        Run interactive mode.
        
        Args:
            directory_path: Directory to operate in
        """
        # Display welcome banner
        display_welcome_banner(self.console, interactive=True)
        
        # Discover files once
        display_info(self.console, "Discovering files...")
        discovery = discover_files(directory_path)
        
        # Parse existing summaries to update file status
        summary_parser = SummaryParser()
        summary_parser.update_file_status(discovery.files_to_process)
        
        while True:
            # Clear screen and show persistent elements
            self.console.clear()
            
            # Show header
            self.console.print("[bold cyan]🎯 codectx - Interactive Mode[/bold cyan]\n")
            
            # Show summary stats
            summary_panel = create_discovery_summary_panel(discovery)
            self.console.print(summary_panel)
            self.console.print()
            
            # Show the file table (limited view in menu)
            file_table = create_file_table(
                discovery.files_to_process, 
                title="📂 Project Files Status",
                show_all=True
            )
            self.console.print(file_table)
            self.console.print()
            
            # Show menu
            choice = self._show_menu(discovery)
            
            if choice == "quit":
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
                
            elif choice == "scan":
                # Get scan options
                scan_config = self._get_scan_options()
                
                if scan_config.get("cancelled"):
                    self.console.print("\n[yellow]❌ Scan cancelled[/yellow]")
                    self.console.print("[dim]Press Enter to continue...[/dim]")
                    input()
                    continue
                
                # Run the scan with live table updates
                try:
                    self._run_scan_with_live_updates(discovery, scan_config)
                    
                    # Ask if user wants to continue
                    self.console.print("\n")
                    continue_choice = inquirer.confirm(
                        message="Scan complete! Return to menu?",
                        default=True
                    ).execute()
                    
                    if not continue_choice:
                        break
                        
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]⚠️ Scan interrupted by user[/yellow]")
                    self.console.print("[dim]Press Enter to return to menu...[/dim]")
                    input()
                    continue
                except Exception as e:
                    display_error(self.console, f"Error during scan: {e}")
                    self.console.print("[dim]Press Enter to return to menu...[/dim]")
                    input()
                    continue
            
            elif choice == "update":
                # Get outdated files (this should already be calculated by menu, but double-check)
                outdated_files = summary_parser.get_outdated_files(discovery.files_to_process)
                updated_files = summary_parser.get_updated_files(discovery.files_to_process)
                
                if not outdated_files:
                    self.console.print("\n[green]✅ All files are up to date! No processing needed.[/green]")
                    self.console.print("[dim]Press Enter to continue...[/dim]")
                    input()
                    continue
                
                # Show summary
                self.console.print(f"\n[yellow]⚠️  Found {len(outdated_files)} outdated files[/yellow]")
                self.console.print(f"[green]✅ {len(updated_files)} files are up to date[/green]")
                
                # Get update options
                update_config = self._get_update_options()
                
                if update_config.get("cancelled"):
                    self.console.print("\n[yellow]❌ Update cancelled[/yellow]")
                    self.console.print("[dim]Press Enter to continue...[/dim]")
                    input()
                    continue
                
                # Run the update with live table updates
                try:
                    self._run_update_with_live_updates(outdated_files, discovery, update_config)
                    
                    # Refresh file status after update
                    summary_parser.update_file_status(discovery.files_to_process)
                    
                    # Ask if user wants to continue
                    self.console.print("\n")
                    continue_choice = inquirer.confirm(
                        message="Update complete! Return to menu?",
                        default=True
                    ).execute()
                    
                    if not continue_choice:
                        break
                        
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]⚠️ Update interrupted by user[/yellow]")
                    self.console.print("[dim]Press Enter to return to menu...[/dim]")
                    input()
                    continue
                except Exception as e:
                    display_error(self.console, f"Error during update: {e}")
                    self.console.print("[dim]Press Enter to return to menu...[/dim]")
                    input()
                    continue
            
            elif choice == "options":
                self.console.print(f"\n[yellow]🚧 Options feature coming soon![/yellow]")
                self.console.print("[dim]This feature will be available in a future release.[/dim]")
                
                # Wait for user acknowledgment
                self.console.print("[dim]Press Enter to continue...[/dim]")
                input()
    
    def _show_menu(self, discovery) -> str:
        """
        Display interactive menu and return user choice.
        
        Args:
            discovery: DiscoveryResult object to check file status
        
        Returns:
            Selected menu option
        """
        self.console.print("\n")
        
        # Count outdated files for dynamic menu
        outdated_files = [f for f in discovery.files_to_process if f.is_outdated()]
        outdated_count = len(outdated_files)
        
        # Create dynamic update option
        if outdated_count == 0:
            update_option = {
                "name": "🔄 Update changed files", 
                "value": "update", 
                "disabled": "(All files up to date)"
            }
            default_choice = "scan"
        else:
            update_option = {
                "name": f"🔄 Update changed files ({outdated_count} files)", 
                "value": "update"
            }
            default_choice = "update"
        
        choices = [
            update_option,
            {"name": "🔍 Scan all files", "value": "scan"},
            {"name": "⚙️  Options", "value": "options", "disabled": "(Coming soon)"},
            {"name": "❌ Quit", "value": "quit"}
        ]
        
        selection = inquirer.select(
            message="What would you like to do?",
            choices=choices,
            default=default_choice,
            pointer="👉",
            instruction="(Use arrow keys to navigate, Enter to select)"
        ).execute()
        
        return selection
    
    def _get_scan_options(self) -> Dict[str, Any]:
        """
        Get scan options from user in interactive mode.
        
        Returns:
            Dictionary with scan configuration
        """
        self.console.print("\n[bold cyan]📋 Scan Configuration[/bold cyan]")
        
        # Ask for scan mode
        mode = inquirer.select(
            message="Choose scan mode:",
            choices=[
                {"name": "🤖 AI Summarization (uses API)", "value": "normal"},
                {"name": "📋 Mock mode (for testing)", "value": "mock"},
                {"name": "📄 Copy mode (raw content only)", "value": "copy"}
            ],
            default="normal",
            pointer="👉"
        ).execute()
        
        # Confirm before proceeding
        if mode == "normal":
            proceed = inquirer.confirm(
                message="This will use your AI API. Continue?",
                default=True
            ).execute()
            
            if not proceed:
                return {"cancelled": True}
        
        return {
            "mode": mode,
            "mock_mode": mode == "mock",
            "copy_mode": mode == "copy",
            "cancelled": False
        }
    
    def _run_scan_with_live_updates(self, discovery, scan_config: Dict[str, Any]) -> None:
        """
        Run scan with live table updates.
        
        Args:
            discovery: DiscoveryResult object
            scan_config: Scan configuration dictionary
        """
        # Clear screen for processing
        self.console.clear()
        self.console.print("[bold cyan]🎯 codectx - Live Processing[/bold cyan]\n")
        
        # Show mode being used
        mode_text = {
            True: "[yellow]🤖 Mock Mode[/yellow] (testing)",
            False: "[green]🤖 AI Summarization[/green]" if not scan_config["copy_mode"] else "[blue]📄 Copy Mode[/blue] (raw content)"
        }[scan_config["mock_mode"]]
        
        self.console.print(f"[bold green]🚀 Processing {len(discovery.files_to_process)} files with {mode_text}[/bold green]\n")
        
        # Determine processing mode
        if scan_config["mock_mode"]:
            mode = ProcessingMode.MOCK
        elif scan_config["copy_mode"]:
            mode = ProcessingMode.COPY
        else:
            mode = ProcessingMode.AI_SUMMARIZATION
        
        # Create configuration
        config = ProcessingConfig(
            mode=mode,
            directory_path=discovery.directory,
            output_file=getattr(self, 'codectx_config', None).output_filename if hasattr(self, 'codectx_config') and self.codectx_config else "codectx.md"
        )
        
        # Create processor
        processor = FileProcessor(config, getattr(self, 'codectx_config', None), None)
        
        # Initialize progress bar
        progress = Progress(console=self.console)
        task = progress.add_task("Processing files", total=len(discovery.files_to_process))
        
        # Process files with live updates
        with Live(
            create_live_processing_layout(discovery.files_to_process, discovery.directory, progress),
            refresh_per_second=4,
            console=self.console
        ) as live:
            for file_info in discovery.files_to_process:
                # Process the file
                result = processor.process_file(file_info)
                
                # Update progress and display
                progress.update(task, advance=1)
                live.update(create_live_processing_layout(discovery.files_to_process, discovery.directory, progress))
        
        # Write output
        try:
            processor.write_output()
            display_processing_complete(
                self.console,
                len(discovery.files_to_process),
                config.output_file
            )
        except Exception as e:
            display_error(self.console, f"Error writing output: {e}")
    
    def _get_update_options(self) -> Dict[str, Any]:
        """
        Get update options from user in interactive mode.
        
        Returns:
            Dictionary with update configuration
        """
        self.console.print("\n[bold cyan]📋 Update Configuration[/bold cyan]")
        
        # Ask for update mode
        mode = inquirer.select(
            message="Choose update mode:",
            choices=[
                {"name": "🤖 AI Summarization (uses API)", "value": "normal"},
                {"name": "📋 Mock mode (for testing)", "value": "mock"},
                {"name": "📄 Copy mode (raw content only)", "value": "copy"}
            ],
            default="normal",
            pointer="👉"
        ).execute()
        
        # Confirm before proceeding
        if mode == "normal":
            proceed = inquirer.confirm(
                message="This will use your AI API for outdated files. Continue?",
                default=True
            ).execute()
            
            if not proceed:
                return {"cancelled": True}
        
        return {
            "mode": mode,
            "mock_mode": mode == "mock",
            "copy_mode": mode == "copy",
            "cancelled": False
        }
    
    def _run_update_with_live_updates(self, outdated_files: List[FileInfo], discovery, update_config: Dict[str, Any]) -> None:
        """
        Run update with live table updates.
        
        Args:
            outdated_files: List of files that need updating
            discovery: DiscoveryResult object
            update_config: Update configuration dictionary
        """
        # Clear screen for processing
        self.console.clear()
        self.console.print("[bold cyan]🎯 codectx - Live Update Processing[/bold cyan]\n")
        
        # Show mode being used
        mode_text = {
            True: "[yellow]🤖 Mock Mode[/yellow] (testing)",
            False: "[green]🤖 AI Summarization[/green]" if not update_config["copy_mode"] else "[blue]📄 Copy Mode[/blue] (raw content)"
        }[update_config["mock_mode"]]
        
        self.console.print(f"[bold green]🚀 Updating {len(outdated_files)} outdated files with {mode_text}[/bold green]\n")
        
        # Determine processing mode
        if update_config["mock_mode"]:
            mode = ProcessingMode.MOCK
        elif update_config["copy_mode"]:
            mode = ProcessingMode.COPY
        else:
            mode = ProcessingMode.AI_SUMMARIZATION
        
        # Create configuration
        config = ProcessingConfig(
            mode=mode,
            directory_path=discovery.directory,
            output_file=getattr(self, 'codectx_config', None).output_filename if hasattr(self, 'codectx_config') and self.codectx_config else "codectx.md"
        )
        
        # Create processor
        processor = FileProcessor(config, getattr(self, 'codectx_config', None), None)
        
        # Initialize progress bar
        progress = Progress(console=self.console)
        task = progress.add_task("Updating files", total=len(outdated_files))
        
        # Process files with live updates
        with Live(
            create_live_processing_layout(discovery.files_to_process, discovery.directory, progress),
            refresh_per_second=4,
            console=self.console
        ) as live:
            for file_info in outdated_files:
                # Process the file
                result = processor.process_file(file_info)
                
                # Update progress and display
                progress.update(task, advance=1)
                live.update(create_live_processing_layout(discovery.files_to_process, discovery.directory, progress))
        
        # Write output
        try:
            processor.write_output()
            display_processing_complete(
                self.console,
                len(outdated_files),
                config.output_file
            )
        except Exception as e:
            display_error(self.console, f"Error writing output: {e}")


def run_interactive_mode(directory_path: str = ".", codectx_config=None) -> None:
    """
    Run interactive mode.
    
    Args:
        directory_path: Directory to operate in
        codectx_config: Optional CodectxConfig object with advanced settings
    """
    from ..utils.configuration import get_config
    
    # Use provided config or load default
    if codectx_config is None:
        codectx_config = get_config()
        
    interactive_mode = InteractiveMode()
    interactive_mode.codectx_config = codectx_config  # Pass the config to the mode
    interactive_mode.run(directory_path)