"""
CLI commands for Sutra-Markdown V2
"""

import typer
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from sutra.monitoring import get_tracker

app = typer.Typer(
    name="sutra",
    help="Revolutionary document-to-markdown converter with Universal AI-Guided Extraction",
    add_completion=False,
)

console = Console()


@app.command()
def convert(
    file_path: Path = typer.Argument(..., help="Path to the document to convert"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path (auto-generated if not specified)"),
    formats: Optional[str] = typer.Option("markdown", "--formats", help="Comma-separated list of output formats: markdown,json,xml,csv,yaml,html"),
    format: Optional[str] = typer.Option(None, "--format", help="Single output format (alternative to --formats)"),
    tier: Optional[str] = typer.Option("auto", "--tier", help="Force specific conversion tier: auto, tier1, tier2, tier3"),
    enable_intelligence: bool = typer.Option(True, "--intelligence/--no-intelligence", help="Enable Universal AI-Guided Extraction"),
    quality: str = typer.Option("high", "--quality", help="Quality setting: high, medium, fast"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output with processing details"),
    show_stats: bool = typer.Option(False, "--show-stats", help="Show processing statistics"),
):
    """
    Convert a single document to markdown and other structured formats.
    
    Examples:
    
        # Basic markdown conversion
        sutra convert document.pdf
        
        # Multiple output formats
        sutra convert document.pdf --formats markdown,json,xml
        
        # Specific format only
        sutra convert document.pdf --format json -o output.json
        
        # All available formats
        sutra convert document.pdf --formats all
        
        # With custom output location
        sutra convert document.pdf --formats json,xml -o output_dir/
        
        # Force specific tier
        sutra convert document.pdf --tier tier1 --format json
        
        # Disable AI enhancement (faster but lower quality)
        sutra convert document.pdf --no-intelligence
    
    Available Output Formats:
    
        📄 markdown - Traditional markdown format (default)
        📋 json     - Structured semantic content with hierarchy
        🏷️  xml      - Hierarchical XML document structure  
        📊 csv      - Tabular data extraction for analysis
        📝 yaml     - Human-readable structured format
        🌐 html     - Rich formatted web output
        
    Format Use Cases:
    
        markdown → Documentation, websites, README files
        json     → API integration, data processing, automation
        xml      → Enterprise systems, data exchange
        csv      → Spreadsheets, databases, data analysis
        yaml     → Configuration files, metadata
        html     → Web rendering, rich display
    """
    try:
        # Parse formats
        if format:
            requested_formats = [format]
        else:
            if formats == "all":
                requested_formats = ["markdown", "json", "xml", "csv", "yaml", "html"]
            else:
                requested_formats = [f.strip() for f in formats.split(",")]
        
        if verbose:
            console.print(f"[cyan]Converting:[/cyan] {file_path}")
            console.print(f"[cyan]Formats:[/cyan] {', '.join(requested_formats)}")
            console.print(f"[cyan]AI Enhancement:[/cyan] {'Enabled' if enable_intelligence else 'Disabled'}")
            console.print(f"[cyan]Quality:[/cyan] {quality}")
            console.print()
        
        # TODO: Implement actual conversion logic
        console.print("[yellow]⚠️  Convert command implementation in progress[/yellow]")
        console.print(f"[dim]Would convert: {file_path} to formats: {', '.join(requested_formats)}[/dim]")
        
        if show_stats:
            console.print("\n[cyan]📊 Processing Statistics:[/cyan]")
            console.print("[dim]Stats would be shown here after implementation[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def convert_batch(
    files_pattern: str = typer.Argument(..., help="Glob pattern for files to convert (e.g., 'docs/*.pdf')"),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir", help="Output directory (auto-generated if not specified)"),
    formats: str = typer.Option("markdown,json", "--formats", help="Comma-separated list of output formats"),
    parallel: bool = typer.Option(True, "--parallel/--sequential", help="Process files in parallel"),
    max_workers: int = typer.Option(4, "--workers", help="Maximum number of parallel workers"),
    enable_intelligence: bool = typer.Option(True, "--intelligence/--no-intelligence", help="Enable Universal AI-Guided Extraction"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
):
    """
    Convert multiple documents in batch with structured output formats.
    
    Examples:
    
        # Convert all PDFs in directory
        sutra convert-batch "documents/*.pdf"
        
        # Multiple formats to specific directory  
        sutra convert-batch "docs/*.pdf" --formats markdown,json,xml -o output/
        
        # Sequential processing (lower memory usage)
        sutra convert-batch "reports/*.pdf" --sequential
        
        # High performance batch processing
        sutra convert-batch "archive/*.pdf" --workers 8 --formats json
    
    Output Structure:
    
        For each input file, generates multiple format files:
        document.pdf → document.md, document.json, document.xml, etc.
    """
    try:
        requested_formats = [f.strip() for f in formats.split(",")]
        
        if verbose:
            console.print(f"[cyan]Pattern:[/cyan] {files_pattern}")
            console.print(f"[cyan]Output Dir:[/cyan] {output_dir or 'auto-generated'}")
            console.print(f"[cyan]Formats:[/cyan] {', '.join(requested_formats)}")
            console.print(f"[cyan]Workers:[/cyan] {max_workers if parallel else 1}")
            console.print()
        
        # TODO: Implement batch conversion
        console.print("[yellow]⚠️  Batch convert command implementation in progress[/yellow]")
        console.print(f"[dim]Would convert files matching: {files_pattern}[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def analyze(
    file_path: Path = typer.Argument(..., help="Path to the document to analyze"),
    show_structure: bool = typer.Option(True, "--structure/--no-structure", help="Show document structure analysis"),
    show_complexity: bool = typer.Option(True, "--complexity/--no-complexity", help="Show complexity analysis"),
    show_patterns: bool = typer.Option(False, "--patterns", help="Show AI-discovered patterns"),
    enable_intelligence: bool = typer.Option(True, "--intelligence/--no-intelligence", help="Enable Universal AI analysis"),
):
    """
    Analyze document without converting - see what Sutra's AI discovers.
    
    Examples:
    
        # Basic analysis
        sutra analyze document.pdf
        
        # Detailed AI pattern analysis
        sutra analyze complex_report.pdf --patterns
        
        # Structure only
        sutra analyze document.pdf --no-complexity
    
    Shows:
    
        📊 Document complexity score and recommended tier
        🏗️  Document structure (headings, sections, elements)
        🧠 AI-discovered patterns (paragraph markers, flow type)
        🎯 Optimal extraction strategy recommendation
        ⚡ Estimated processing time and cost
    """
    try:
        console.print(f"[cyan]Analyzing:[/cyan] {file_path}")
        console.print()
        
        # TODO: Implement analysis
        console.print("[yellow]⚠️  Analyze command implementation in progress[/yellow]")
        console.print(f"[dim]Would analyze: {file_path}[/dim]")
        
        if show_structure:
            console.print("\n[cyan]📄 Document Structure:[/cyan]")
            console.print("[dim]Structure analysis would be shown here[/dim]")
        
        if show_complexity:
            console.print("\n[cyan]🧮 Complexity Analysis:[/cyan]")
            console.print("[dim]Complexity scoring would be shown here[/dim]")
            
        if show_patterns:
            console.print("\n[cyan]🧠 AI Patterns Discovered:[/cyan]")
            console.print("[dim]AI pattern analysis would be shown here[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def formats():
    """
    List all available output formats with descriptions and use cases.
    """
    formats_table = Table(title="🎯 Available Output Formats", box=box.ROUNDED)
    formats_table.add_column("Format", style="cyan", no_wrap=True)
    formats_table.add_column("Extension", style="yellow", no_wrap=True)
    formats_table.add_column("Description", style="white")
    formats_table.add_column("Use Cases", style="green")
    
    format_data = [
        ("markdown", ".md", "Traditional markdown format", "Documentation, websites, README files"),
        ("json", ".json", "Structured semantic content with hierarchy", "API integration, data processing, automation"),
        ("xml", ".xml", "Hierarchical XML document structure", "Enterprise systems, data exchange, workflows"),
        ("csv", ".csv", "Tabular data extraction for analysis", "Spreadsheets, databases, data analysis"),
        ("yaml", ".yaml", "Human-readable structured format", "Configuration files, metadata, DevOps"),
        ("html", ".html", "Rich formatted web output", "Web rendering, rich display, presentations"),
    ]
    
    for fmt, ext, desc, use_cases in format_data:
        formats_table.add_row(fmt, ext, desc, use_cases)
    
    console.print(formats_table)
    
    console.print(f"\n[cyan]💡 Pro Tips:[/cyan]")
    console.print("• Use [yellow]--formats all[/yellow] to generate all formats at once")
    console.print("• JSON format includes semantic structure with 95+ element types")
    console.print("• CSV format is perfect for data analysis and visualization")
    console.print("• XML format preserves document hierarchy for enterprise systems")
    console.print("• YAML format is most human-readable for configuration")
    console.print("• HTML format includes styling for rich web display")


@app.command()
def serve(
    host: str = typer.Option("localhost", "--host", help="Host to bind the server"),
    port: int = typer.Option(8000, "--port", help="Port to bind the server"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
    workers: int = typer.Option(1, "--workers", help="Number of worker processes"),
):
    """
    Start the Sutra API server for web-based document conversion.
    
    Examples:
    
        # Development server with auto-reload
        sutra serve --reload
        
        # Production server on all interfaces
        sutra serve --host 0.0.0.0 --port 8000 --workers 4
        
        # Custom configuration
        sutra serve --host localhost --port 3000
    
    Access:
    
        🌐 API: http://localhost:8000
        📚 Docs: http://localhost:8000/docs
        🔧 Health: http://localhost:8000/health
    """
    try:
        import uvicorn
        console.print(f"[cyan]🚀 Starting Sutra API server...[/cyan]")
        console.print(f"[cyan]📡 Host:[/cyan] {host}")
        console.print(f"[cyan]🔌 Port:[/cyan] {port}")
        console.print(f"[cyan]👥 Workers:[/cyan] {workers}")
        console.print(f"[cyan]🔄 Reload:[/cyan] {reload}")
        console.print()
        
        uvicorn.run(
            "sutra.api.app:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1
        )
        
    except ImportError:
        console.print("[red]❌ Error:[/red] uvicorn not installed. Install with: pip install uvicorn")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error starting server:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def usage():
    """
    Display Nomic API usage statistics
    
    Shows comprehensive tracking of:
    - Total embeddings used
    - Monthly usage vs free tier limit
    - Cost estimates
    - Usage projections
    """
    tracker = get_tracker()
    summary = tracker.get_summary()
    
    # Create main stats table
    stats_table = Table(title="📊 Nomic API Usage", box=box.ROUNDED)
    stats_table.add_column("Metric", style="cyan", no_wrap=True)
    stats_table.add_column("Value", style="magenta")
    
    stats_table.add_row("Total Embeddings", f"{summary['total_embeddings']:,}")
    stats_table.add_row("├─ Text", f"{summary['text_embeddings']:,}")
    stats_table.add_row("└─ Multimodal", f"{summary['multimodal_embeddings']:,}")
    stats_table.add_row("Documents Processed", f"{summary['documents_processed']:,}")
    stats_table.add_row("Estimated Cost", summary['estimated_cost'])
    
    console.print(stats_table)
    
    # Monthly usage panel
    usage_pct = float(summary['usage_percentage'].rstrip('%'))
    if usage_pct >= 95:
        status_style = "bold red"
        status_emoji = "🚨"
    elif usage_pct >= 80:
        status_style = "bold yellow"
        status_emoji = "⚠️"
    elif usage_pct >= 50:
        status_style = "bold blue"
        status_emoji = "📊"
    else:
        status_style = "bold green"
        status_emoji = "✅"
    
    monthly_panel = Panel(
        f"""[{status_style}]{status_emoji} {summary['status']}[/{status_style}]
        
Usage: {summary['monthly_usage']:,} / {summary['monthly_limit']:,} ({summary['usage_percentage']})
Remaining: {summary['remaining']:,} embeddings

Avg Daily: {summary['avg_daily_usage']:,} embeddings
Days Until Limit: {summary['days_until_limit']}""",
        title="📅 This Month",
        border_style=status_style,
        box=box.ROUNDED
    )
    console.print("\n", monthly_panel)
    
    # Session stats
    session_table = Table(title="💻 Current Session", box=box.ROUNDED)
    session_table.add_column("Metric", style="cyan")
    session_table.add_column("Value", style="green")
    
    session_table.add_row("Embeddings", f"{summary['session_embeddings']:,}")
    session_table.add_row("Documents", f"{summary['session_documents']:,}")
    
    console.print("\n", session_table)
    
    # Document type breakdown
    if summary['by_document_type']:
        doc_type_table = Table(title="📄 By Document Type", box=box.ROUNDED)
        doc_type_table.add_column("Type", style="cyan")
        doc_type_table.add_column("Count", style="magenta", justify="right")
        
        for doc_type, count in sorted(
            summary['by_document_type'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            doc_type_table.add_row(doc_type, f"{count:,}")
        
        console.print("\n", doc_type_table)
    
    # Last 7 days
    if summary['last_7_days']:
        days_table = Table(title="📈 Last 7 Days", box=box.ROUNDED)
        days_table.add_column("Date", style="cyan")
        days_table.add_column("Embeddings", style="magenta", justify="right")
        
        for date, count in sorted(summary['last_7_days'].items(), reverse=True):
            days_table.add_row(date, f"{count:,}")
        
        console.print("\n", days_table)
    
    console.print()


@app.command()
def version():
    """Display version information"""
    from sutra import __version__
    console.print(f"[bold cyan]Sutra-Markdown[/bold cyan] v{__version__}")
    console.print("[dim]Revolutionary document-to-markdown converter[/dim]")


@app.command()
def info():
    """Display system information"""
    import sys
    import platform
    
    info_table = Table(title="ℹ️  System Information", box=box.ROUNDED)
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Value", style="magenta")
    
    info_table.add_row("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    info_table.add_row("Platform", platform.platform())
    info_table.add_row("Architecture", platform.machine())
    
    console.print(info_table)


if __name__ == "__main__":
    app()
