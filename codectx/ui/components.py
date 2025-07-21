"""
Reusable UI components for codectx
"""
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.live import Live
from rich.console import Group

from ..core.models import FileInfo, DiscoveryResult, ProcessingStats, ProcessingStatus
from ..utils.utils import get_timestamp


def create_file_table(
    files: List[FileInfo], 
    title: str = "📂 Project Files Overview",
    show_all: bool = False,
    max_display: int = 15
) -> Table:
    """
    Create a Rich table from file information.
    
    Args:
        files: List of FileInfo objects
        title: Table title
        show_all: Whether to show all files or limit display
        max_display: Maximum files to show when show_all is False
        
    Returns:
        Rich Table object
    """
    table = Table(
        title=title, 
        show_header=True, 
        header_style="bold cyan",
        title_style="bold magenta",
        border_style="blue"
    )
    table.add_column("📁 File Path", style="white", width=38)
    table.add_column("📏 Size", justify="right", style="cyan", width=8)
    table.add_column("📅 Modified", justify="center", width=14)
    table.add_column("🕒 Last Summary", justify="center", width=14)
    table.add_column("📊 Status", justify="center", width=22)
    
    # Show either all files or limited view
    display_files = files if show_all else files[:max_display]
    
    for file_info in display_files:
        # Determine if file is outdated for color coding
        is_outdated = file_info.is_outdated() if hasattr(file_info, 'is_outdated') else False
        
        # Map status to display string with better labels and icons
        status_display = {
            ProcessingStatus.PENDING: "[yellow]⏳  Ready[/yellow]",
            ProcessingStatus.PROCESSING: "[yellow]🔄  Processing...[/yellow]",
            ProcessingStatus.COMPLETED: "[green]✅  Complete[/green]",
            ProcessingStatus.COPIED: "[blue]📝  Copied[/blue]",
            ProcessingStatus.ERROR: f"[red]❌  {file_info.error_message[:10] if file_info.error_message else 'Error'}...[/red]",
            ProcessingStatus.UPDATED: "[green]🔗  Up to date[/green]",
            ProcessingStatus.OUTDATED: "[red]⚠️  Needs update[/red]"
        }[file_info.status]
        
        # Color-code dates based on status
        if is_outdated and file_info.summary_date_str:
            # Red dates for outdated files
            modified_display = f"[red]{file_info.modified_str}[/red]"
            summary_date_display = f"[red]{file_info.summary_date_str}[/red]"
        elif file_info.summary_date_str:
            # Normal dates for up-to-date files
            modified_display = file_info.modified_str
            summary_date_display = f"[green]{file_info.summary_date_str}[/green]"
        else:
            # No summary yet
            modified_display = file_info.modified_str
            summary_date_display = "[dim]Never[/dim]"
        
        # Style the file path based on status
        if file_info.status == ProcessingStatus.ERROR:
            path_display = f"[dim red]{file_info.display_path}[/dim red]"
        elif is_outdated:
            path_display = f"[bold]{file_info.display_path}[/bold]"
        else:
            path_display = file_info.display_path
        
        table.add_row(
            path_display,
            file_info.size_str,
            modified_display,
            summary_date_display,
            status_display
        )
    
    # Add summary row if there are more files and we're in limited view
    if not show_all and len(files) > max_display:
        remaining = len(files) - max_display
        table.add_row(
            f"[dim]... and {remaining} more files[/dim]",
            "",
            "",
            "",
            "[dim]Ready[/dim]"
        )
    
    return table


def create_discovery_summary_panel(discovery: DiscoveryResult) -> Panel:
    """
    Create a panel with discovery summary statistics.
    
    Args:
        discovery: DiscoveryResult object
        
    Returns:
        Rich Panel with summary stats
    """
    # Calculate status counts for better summary
    total_files = len(discovery.files_to_process)
    updated_files = len([f for f in discovery.files_to_process if hasattr(f, 'status') and f.status == ProcessingStatus.UPDATED])
    outdated_files = len([f for f in discovery.files_to_process if hasattr(f, 'status') and f.status == ProcessingStatus.OUTDATED])
    
    stats_text = (
        f"[bold cyan]📂 Directory:[/bold cyan] {discovery.directory}\n"
        f"[green]🔗 Up to date:[/green] {updated_files} | "
        f"[red]⚠️ Need updates:[/red] {outdated_files} | "
        f"[yellow]🚫 Ignored:[/yellow] {len(discovery.ignored_files)} | "
        f"[blue]🎯 Patterns:[/blue] {discovery.ignore_patterns_count}"
    )
    
    return Panel(
        stats_text,
        title="📊 Summary",
        border_style="blue",
        padding=(0, 1)
    )


def create_processing_stats_panel(stats: ProcessingStats, directory: str) -> Panel:
    """
    Create a panel with live processing statistics.
    
    Args:
        stats: ProcessingStats object
        directory: Directory being processed
        
    Returns:
        Rich Panel with live stats
    """
    stats_text = (
        f"[bold cyan]📂 Processing:[/bold cyan] {directory}\n"
        f"[green]✅ Completed:[/green] {stats.completed} | "
        f"[yellow]🔄 Processing:[/yellow] {stats.processing} | "
        f"[cyan]📋 Pending:[/cyan] {stats.pending}"
    )
    
    if stats.errors > 0:
        stats_text += f" | [red]❌ Errors:[/red] {stats.errors}"
    
    return Panel(
        stats_text,
        title="📊 Live Status",
        border_style="blue",
        padding=(0, 1)
    )


def create_live_processing_layout(
    files: List[FileInfo],
    directory: str,
    progress: Progress
) -> Group:
    """
    Create a live layout for processing display.
    
    Args:
        files: List of files being processed
        directory: Directory being processed
        progress: Rich Progress object
        
    Returns:
        Rich Group layout
    """
    # Calculate stats
    stats = ProcessingStats(total=len(files))
    stats.update_from_files(files)
    
    # Create components
    stats_panel = create_processing_stats_panel(stats, directory)
    files_table = create_file_table(files, show_all=True)
    
    return Group(
        stats_panel,
        "",
        files_table,
        "",
        progress
    )


def display_welcome_banner(console: Console, interactive: bool = True) -> None:
    """
    Display the welcome banner with ASCII art.
    
    Args:
        console: Rich Console object
        interactive: Whether this is interactive mode
    """
    console.print("\n[bold magenta]Welcome to codectx![/bold magenta]")
    console.print("""
 ██████╗ ██████╗ ██████╗ ███████╗ ██████╗████████╗██╗  ██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝╚══██╔══╝╚██╗██╔╝
██║     ██║   ██║██║  ██║█████╗  ██║        ██║    ╚███╔╝ 
██║     ██║   ██║██║  ██║██╔══╝  ██║        ██║    ██╔██╗ 
╚██████╗╚██████╔╝██████╔╝███████╗╚██████╗   ██║   ██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
""")
    
    if interactive:
        console.print("[bold cyan]🎯 Interactive Mode[/bold cyan]")
        console.print("[dim]Tip: Use command-line arguments for direct execution in scripts[/dim]\n")
    else:
        console.print("[bold cyan]AI-powered code context & summarization tool[/bold cyan]")
        from .. import __version__
        console.print(f"[dim]Version {__version__}[/dim]\n")


def display_processing_complete(console: Console, file_count: int, output_file: str = "codectx.md") -> None:
    """
    Display processing completion message.
    
    Args:
        console: Rich Console object
        file_count: Number of files processed
        output_file: Output file name
    """
    console.print(f"\n{get_timestamp()} [green]✅ Processing complete! {file_count} files processed.[/green]")
    console.print(f"{get_timestamp()} [green]Output written to {output_file}[/green]")


def display_error(console: Console, message: str) -> None:
    """
    Display an error message with timestamp.
    
    Args:
        console: Rich Console object
        message: Error message
    """
    console.print(f"{get_timestamp()} [red]❌ Error: {message}[/red]")


def display_info(console: Console, message: str) -> None:
    """
    Display an info message with timestamp.
    
    Args:
        console: Rich Console object
        message: Info message
    """
    console.print(f"{get_timestamp()} [cyan]{message}[/cyan]")


def display_warning(console: Console, message: str) -> None:
    """
    Display a warning message with timestamp.
    
    Args:
        console: Rich Console object
        message: Warning message
    """
    console.print(f"{get_timestamp()} [yellow]⚠️ {message}[/yellow]")