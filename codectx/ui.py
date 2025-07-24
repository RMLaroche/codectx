"""
User interface components for codectx

This module provides rich console UI components including:
- Welcome banner and status messages
- File status tables with color-coded information
- Live processing displays with real-time updates
- Progress tracking and completion statistics
- Consistent styling and formatting across all UI elements
"""
from typing import List, Dict
from datetime import datetime
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.live import Live

from .discovery import FileInfo, DiscoveryResult
from .constants import DEFAULT_TABLE_WIDTH, PROCESSING_REFRESH_RATE


def display_welcome() -> None:
    """Display welcome banner"""
    console = Console()
    console.print("\n[bold magenta]Welcome to codectx![/bold magenta]")
    console.print("""
 ██████╗ ██████╗ ██████╗ ███████╗ ██████╗████████╗██╗  ██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝╚══██╔══╝╚██╗██╔╝
██║     ██║   ██║██║  ██║█████╗  ██║        ██║    ╚███╔╝ 
██║     ██║   ██║██║  ██║██╔══╝  ██║        ██║    ██╔██╗ 
╚██████╗╚██████╔╝██████╔╝███████╗╚██████╗   ██║   ██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
""")
    console.print("[bold cyan]AI-powered code context & summarization tool[/bold cyan]")
    
    # Import version here to avoid circular imports
    try:
        from . import __version__
        console.print(f"[dim]Version {__version__}[/dim]\n")
    except ImportError:
        console.print("[dim]Version 1.0.0[/dim]\n")


def display_info(message: str) -> None:
    """Display info message with timestamp"""
    console = Console()
    timestamp = _get_timestamp()
    console.print(f"{timestamp} [cyan]{message}[/cyan]")


def display_success(message: str) -> None:
    """Display success message with timestamp"""
    console = Console()
    timestamp = _get_timestamp()
    console.print(f"{timestamp} [green]{message}[/green]")


def display_warning(message: str) -> None:
    """Display warning message with timestamp"""
    console = Console()
    timestamp = _get_timestamp()
    console.print(f"{timestamp} [yellow]⚠️ {message}[/yellow]")


def display_error(message: str) -> None:
    """Display error message with timestamp"""
    console = Console()
    timestamp = _get_timestamp()
    console.print(f"{timestamp} [red]❌ Error: {message}[/red]")


def display_file_stats(discovery: DiscoveryResult, file_status: Dict[str, str]) -> None:
    """Display file statistics"""
    console = Console()
    
    # Count files by status
    status_counts = {"up-to-date": 0, "outdated": 0, "new": 0}
    for status in file_status.values():
        if status in status_counts:
            status_counts[status] += 1
    
    console.print()
    console.print("[green]📊 File Analysis Complete[/green]")
    console.print(f"[green]✅ Up-to-date:[/green] {status_counts['up-to-date']}")
    console.print(f"[yellow]⚠️  Need updates:[/yellow] {status_counts['outdated']}")
    console.print(f"[blue]📄 Never processed:[/blue] {status_counts['new']}")
    console.print(f"[red]🚫 Ignored:[/red] {len(discovery.ignored_files)} | [blue]🎯 Patterns:[/blue] {discovery.ignore_patterns_count}")
    console.print()


def display_file_table(files: List[FileInfo], file_status: Dict[str, str], title: str = "📂 Project Files") -> None:
    """Display file table with status information"""
    console = Console()
    
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        title_style="bold magenta",
        border_style="blue"
    )
    
    table.add_column("📁 File Path", style="white", width=40)
    table.add_column("📏 Size", justify="right", style="cyan", width=8) 
    table.add_column("📅 Modified", justify="center", width=12)
    table.add_column("📊 Status", justify="center", width=16)
    
    for file_info in files:
        status = file_status.get(file_info.relative_path, "unknown")
        
        # Style based on status
        if status == "up-to-date":
            status_display = "[green]🔗 Up to date[/green]"
            path_display = file_info.relative_path
        elif status == "outdated":
            status_display = "[yellow]⚠️ Needs update[/yellow]"
            path_display = f"[bold]{file_info.relative_path}[/bold]"
        elif status == "new":
            status_display = "[blue]⏳ Pending[/blue]"
            path_display = f"[bold]{file_info.relative_path}[/bold]"
        else:
            status_display = "[dim]Unknown[/dim]"
            path_display = file_info.relative_path
        
        table.add_row(
            path_display,
            file_info.size_str,
            file_info.modified_str,
            status_display
        )
    
    console.print(table)


def display_processing_progress(files: List[FileInfo], mode_name: str = "Processing") -> Progress:
    """Start and return progress bar for processing"""
    console = Console()
    progress = Progress(console=console)
    task = progress.add_task(f"{mode_name} files", total=len(files))
    progress.start()
    return progress


def create_live_processing_layout(files: List[FileInfo], directory: str, progress: Progress) -> Group:
    """Create a live layout for processing display with real-time file status updates"""
    
    # Create processing stats panel
    total_files = len(files)
    completed = len([f for f in files if hasattr(f, '_processing_status') and f._processing_status == 'completed'])
    processing = len([f for f in files if hasattr(f, '_processing_status') and f._processing_status == 'processing'])
    pending = total_files - completed - processing
    errors = len([f for f in files if hasattr(f, '_processing_status') and f._processing_status == 'error'])
    
    stats_text = (
        f"[bold cyan]📂 Processing:[/bold cyan] {directory}\n"
        f"[green]✅ Completed:[/green] {completed} | "
        f"[yellow]🔄 Processing:[/yellow] {processing} | "
        f"[cyan]⏳ Pending:[/cyan] {pending}"
    )
    
    if errors > 0:
        stats_text += f" | [red]❌ Errors:[/red] {errors}"
    
    stats_panel = Panel(
        stats_text,
        title="📊 Live Status",
        border_style="blue",
        padding=(0, 1)
    )
    
    # Create live file status table
    files_table = _create_live_files_table(files)
    
    return Group(
        stats_panel,
        "",
        files_table,
        "",
        progress
    )


def _create_live_files_table(files: List[FileInfo]) -> Table:
    """Create a table showing real-time file processing status"""
    table = Table(
        title="📂 Project Files Overview",
        show_header=True,
        header_style="bold cyan",
        title_style="bold magenta", 
        border_style="blue"
    )
    
    table.add_column("📁 File Path", style="white", width=DEFAULT_TABLE_WIDTH)
    table.add_column("📏 Size", justify="right", style="cyan", width=8)
    table.add_column("📅 Modified", justify="center", width=14)
    table.add_column("📊 Status", justify="center", width=22)
    
    for file_info in files:
        # Get current processing status
        status = getattr(file_info, '_processing_status', 'pending')
        
        # Map status to display
        if status == 'completed':
            status_display = "[green]✅  Complete[/green]"
            path_display = file_info.relative_path
        elif status == 'processing':
            status_display = "[yellow]🔄  Processing...[/yellow]"
            path_display = f"[bold yellow]{file_info.relative_path}[/bold yellow]"
        elif status == 'error':
            status_display = "[red]❌  Error[/red]"
            path_display = f"[dim red]{file_info.relative_path}[/dim red]"
        else:  # pending
            status_display = "[cyan]⏳  Pending[/cyan]"
            path_display = file_info.relative_path
        
        table.add_row(
            path_display,
            file_info.size_str,
            file_info.modified_str,
            status_display
        )
    
    return table


def create_live_processing_context(files: List[FileInfo], directory: str):
    """Create a context manager for live processing display"""
    console = Console()
    progress = Progress(console=console)
    task = progress.add_task("Processing files", total=len(files))
    
    live = Live(
        create_live_processing_layout(files, directory, progress),
        refresh_per_second=PROCESSING_REFRESH_RATE,
        console=console
    )
    
    class LiveContext:
        def __init__(self):
            self.progress = progress
            self.task = task
            self.live = live
            
        def __enter__(self):
            self.live.start()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.live.stop()
            
        def update_file_status(self, file_info: FileInfo, status: str):
            """Update the processing status of a file"""
            file_info._processing_status = status
            self.live.update(create_live_processing_layout(files, directory, self.progress))
            
        def advance_progress(self):
            """Advance the progress bar"""
            self.progress.advance(self.task)
            self.live.update(create_live_processing_layout(files, directory, self.progress))
    
    return LiveContext()


def display_completion_stats(processed_count: int, output_file: str, up_to_date_count: int = 0) -> None:
    """Display completion statistics"""
    console = Console()
    timestamp = _get_timestamp()
    
    console.print()
    console.print(f"{timestamp} [green]✅ Processing complete! {processed_count} files processed.[/green]")
    console.print(f"{timestamp} [green]Output written to {output_file}[/green]")
    
    if up_to_date_count > 0:
        console.print(f"[blue]📄 {up_to_date_count} files were already up to date[/blue]")


def display_status_summary(discovery: DiscoveryResult, file_status: Dict[str, str]) -> None:
    """Display detailed status summary for --status mode"""
    console = Console()
    
    # Count files by status
    status_counts = {"up-to-date": 0, "outdated": 0, "new": 0}
    for status in file_status.values():
        if status in status_counts:
            status_counts[status] += 1
    
    console.print()
    console.print("[green]📊 File Status Summary[/green]")
    console.print(f"[green]✅ Up-to-date:[/green] {status_counts['up-to-date']}")
    console.print(f"[yellow]⚠️  Need updates:[/yellow] {status_counts['outdated']}")
    console.print(f"[blue]📄 Never processed:[/blue] {status_counts['new']}")
    console.print(f"[red]🚫 Ignored:[/red] {len(discovery.ignored_files)} | [blue]🎯 Patterns:[/blue] {discovery.ignore_patterns_count}")
    console.print()
    
    # Filter files that need attention
    files_needing_attention = [
        f for f in discovery.files_to_process
        if file_status.get(f.relative_path) in ["outdated", "new"]
    ]
    
    if len(discovery.files_to_process) <= 20:
        # Show all files for small projects
        display_file_table(discovery.files_to_process, file_status, f"📂 Project Files Status ({len(discovery.files_to_process)} files)")
    else:
        # Show summary panel for large projects
        _display_summary_panel(discovery, status_counts)
        
        if files_needing_attention:
            console.print()
            display_info(f"📋 Files needing attention ({len(files_needing_attention)} of {len(discovery.files_to_process)} total):")
            
            # Show up to 15 files that need attention
            files_to_show = files_needing_attention[:15]
            display_file_table(files_to_show, file_status, "⚠️ Files Requiring Updates")
            
            if len(files_needing_attention) > 15:
                console.print(f"[dim]... and {len(files_needing_attention) - 15} more files need updates[/dim]")
            
            console.print(f"[dim]Use 'codectx' to update outdated files or 'codectx --scan-all' to process all files[/dim]")
        else:
            console.print()
            display_info("🎉 All files are up-to-date! No action needed.")


def _display_summary_panel(discovery: DiscoveryResult, status_counts: Dict[str, int]) -> None:
    """Display summary panel for large projects"""
    console = Console()
    
    stats_text = (
        f"[bold cyan]📂 Directory:[/bold cyan] {discovery.directory}\n"
        f"[green]🔗 Up to date:[/green] {status_counts['up-to-date']} | "
        f"[yellow]⚠️ Need updates:[/yellow] {status_counts['outdated']} | "
        f"[blue]📄 Never processed:[/blue] {status_counts['new']} | "
        f"[red]🚫 Ignored:[/red] {len(discovery.ignored_files)} | "
        f"[blue]🎯 Patterns:[/blue] {discovery.ignore_patterns_count}"
    )
    
    panel = Panel(
        stats_text,
        title="📊 Summary", 
        border_style="blue",
        padding=(0, 1)
    )
    
    console.print(panel)


def _get_timestamp() -> str:
    """Get current timestamp for console output"""
    return f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"