"""Terminal User Interface for the 3D model scraper."""

import re
from pathlib import Path
from typing import List, Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .config import get_config
from .scraper import SketchfabScraper, WoWHeadScraper


class ScraperTUI:
    """Terminal User Interface for model scraping."""

    def __init__(self):
        """Initialize TUI."""
        self.console = Console()
        self.config = get_config()

    def print_header(self) -> None:
        """Print application header."""
        header = """
╔═══════════════════════════════════════════════════════════════════╗
║                   3D Model Scraper - WoWHead Edition               ║
║          Extract & Convert 3D Models to STL Format               ║
╚═══════════════════════════════════════════════════════════════════╝
        """
        self.console.print(header, style="bold cyan")

    def print_menu(self) -> None:
        """Print main menu."""
        menu_table = Table.grid(padding=1)
        menu_table.add_row("[bold]1.[/bold] Extract from WoWHead Dressing Room")
        menu_table.add_row("[bold]2.[/bold] Search & Download from Sketchfab")
        menu_table.add_row("[bold]3.[/bold] Batch Process Multiple URLs")
        menu_table.add_row("[bold]4.[/bold] View Settings")
        menu_table.add_row("[bold]5.[/bold] Exit")

        panel = Panel(
            menu_table,
            title="[bold]Main Menu[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.console.print(panel)

    def get_menu_choice(self) -> str:
        """Get user menu choice."""
        return Prompt.ask("[bold cyan]Select option[/bold cyan]", choices=["1", "2", "3", "4", "5"])

    def wowhead_scraper_menu(self) -> None:
        """WoWHead scraper menu."""
        self.console.print("\n[bold cyan]WoWHead Dressing Room Scraper[/bold cyan]\n")
        self.console.print(
            "[yellow]ℹ️  Paste a WoWHead dressing room URL to extract character models.[/yellow]"
        )
        self.console.print(
            "[yellow]    Example: https://www.wowhead.com/dressing-room#...[/yellow]\n"
        )

        wowhead_url = Prompt.ask("[cyan]WoWHead dressing room URL[/cyan]")

        if not wowhead_url.strip():
            self.console.print("[red]❌ No URL provided[/red]")
            return

        if "wowhead.com" not in wowhead_url and "wowhead.com/dressing-room" not in wowhead_url:
            self.console.print(
                "[red]❌ Invalid URL. Must be a wowhead.com/dressing-room link[/red]"
            )
            return

        # Show processing
        with self.console.status(
            "[bold cyan]🔄 Initializing browser and extracting models...",
            spinner="dots",
        ):
            scraper = WoWHeadScraper(headless=True)
            try:
                model_urls = scraper.extract_model_urls(wowhead_url)
            finally:
                scraper.close()

        if not model_urls:
            self.console.print(
                "[red]❌ No models found. The page may not have loaded correctly.[/red]"
            )
            self.console.print(
                "[yellow]💡 Try:[/yellow]\n"
                "    • Check the URL is correct\n"
                "    • Wait a moment and try again\n"
                "    • Visit the page in a browser first to ensure it loads"
            )
            return

        # Show found models
        self.console.print(f"\n[bold green]✅ Found {len(model_urls)} model(s)[/bold green]\n")

        for i, url in enumerate(model_urls, 1):
            self.console.print(f"[cyan]{i}.[/cyan] {url[:80]}..." if len(url) > 80 else f"[cyan]{i}.[/cyan] {url}")

        # Ask if user wants to download
        download = Confirm.ask("\n[bold cyan]Download and convert these models?[/bold cyan]")
        if not download:
            return

        # Ask for custom name
        base_name = Prompt.ask(
            "[cyan]Base name for models[/cyan]",
            default="wowhead_character",
        )

        # Download and convert
        scraper = WoWHeadScraper(headless=True)
        results = []
        try:
            for i, url in enumerate(model_urls, 1):
                model_name = f"{base_name}_part{i}"
                with self.console.status(
                    f"[bold cyan]📥 Processing model {i}/{len(model_urls)}...",
                    spinner="dots",
                ):
                    result = scraper.download_and_convert(url, model_name)
                    results.append((model_name, result))
        finally:
            scraper.close()

        # Show results
        self.console.print("\n[bold cyan]Results:[/bold cyan]\n")
        success_count = 0
        for name, result in results:
            if result:
                self.console.print(f"[green]✅ {name}[/green] → {result}")
                success_count += 1
            else:
                self.console.print(f"[red]❌ {name}[/red] - Failed to convert")

        self.console.print(
            f"\n[bold]Processed {success_count}/{len(model_urls)} models successfully[/bold]"
        )
        self.console.print(f"[cyan]📂 Output directory: {self.config.output_dir}[/cyan]\n")

    def sketchfab_scraper_menu(self) -> None:
        """Sketchfab scraper menu."""
        self.console.print("\n[bold cyan]Sketchfab Model Search & Download[/bold cyan]\n")

        query = Prompt.ask("[cyan]Search query[/cyan]")
        if not query.strip():
            self.console.print("[red]❌ No query provided[/red]")
            return

        limit = int(
            Prompt.ask(
                "[cyan]Maximum results[/cyan]",
                default="10",
            )
        )

        license_choice = Prompt.ask(
            "[cyan]License filter[/cyan]",
            choices=["cc0", "cc-by", "none"],
            default="cc0",
        )
        license_filter = None if license_choice == "none" else license_choice

        # Search
        with self.console.status(
            "[bold cyan]🔍 Searching Sketchfab...",
            spinner="dots",
        ):
            scraper = SketchfabScraper()
            try:
                models = scraper.search(
                    query=query,
                    license=license_filter,
                    downloadable=True,
                    limit=limit,
                )
            finally:
                scraper.close()

        if not models:
            self.console.print("[red]❌ No models found[/red]")
            return

        # Show results
        self.console.print(f"\n[bold green]✅ Found {len(models)} model(s)[/bold green]\n")

        table = Table(title="Search Results", show_header=True, header_style="bold cyan")
        table.add_column("#", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Views", style="magenta")
        table.add_column("Likes", style="yellow")

        for i, model in enumerate(models[:20], 1):  # Show max 20
            name = model.get("name", "Unknown")[:40]
            views = model.get("viewCount", 0)
            likes = model.get("likeCount", 0)
            table.add_row(str(i), name, str(views), str(likes))

        self.console.print(table)

        # Ask if user wants to download
        if not Confirm.ask(
            "\n[bold cyan]Download and convert models?[/bold cyan]",
            default=False,
        ):
            return

        # Select which models to download
        indices = Prompt.ask(
            "[cyan]Model indices to download (comma-separated, e.g. 1,3,5)[/cyan]",
            default="1",
        )

        try:
            indices = [int(i.strip()) - 1 for i in indices.split(",")]
            selected_models = [models[i] for i in indices if 0 <= i < len(models)]
        except (ValueError, IndexError):
            self.console.print("[red]❌ Invalid selection[/red]")
            return

        # Download and convert
        scraper = SketchfabScraper()
        results = []
        try:
            for i, model in enumerate(selected_models, 1):
                model_id = model.get("uid")
                model_name = model.get("name", "model")
                with self.console.status(
                    f"[bold cyan]📥 Processing {i}/{len(selected_models)}: {model_name}...",
                    spinner="dots",
                ):
                    result = scraper.download_and_convert(model_id, model_name)
                    results.append((model_name, result))
        finally:
            scraper.close()

        # Show results
        self.console.print("\n[bold cyan]Results:[/bold cyan]\n")
        success_count = 0
        for name, result in results:
            if result:
                self.console.print(f"[green]✅ {name}[/green] → {result}")
                success_count += 1
            else:
                self.console.print(f"[red]❌ {name}[/red] - Failed")

        self.console.print(
            f"\n[bold]Downloaded {success_count}/{len(selected_models)} models successfully[/bold]"
        )

    def batch_processor_menu(self) -> None:
        """Batch process multiple URLs."""
        self.console.print("\n[bold cyan]Batch URL Processor[/bold cyan]\n")
        self.console.print(
            "[yellow]Enter URLs one per line. Type 'done' when finished.[/yellow]\n"
        )

        urls = []
        while True:
            url = Prompt.ask("[cyan]URL[/cyan]").strip()
            if url.lower() == "done":
                break
            if url:
                urls.append(url)
                self.console.print(f"[green]✓ Added[/green]")

        if not urls:
            self.console.print("[red]❌ No URLs provided[/red]")
            return

        self.console.print(f"\n[bold]Processing {len(urls)} URLs[/bold]\n")

        base_name = Prompt.ask(
            "[cyan]Base name for models[/cyan]",
            default="batch_model",
        )

        results = []

        for i, url in enumerate(urls, 1):
            model_name = f"{base_name}_{i}"

            with self.console.status(
                f"[bold cyan]📥 Processing {i}/{len(urls)}...",
                spinner="dots",
            ):
                try:
                    if "wowhead.com" in url:
                        scraper = WoWHeadScraper(headless=True)
                        try:
                            result = scraper.download_and_convert(url, model_name)
                        finally:
                            scraper.close()
                    elif "sketchfab.com" in url:
                        scraper = SketchfabScraper()
                        try:
                            result = scraper.download_and_convert(url, model_name)
                        finally:
                            scraper.close()
                    else:
                        self.console.print(
                            f"[yellow]⚠️  Skipping unknown source: {url}[/yellow]"
                        )
                        result = None

                    results.append((model_name, result))
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    results.append((model_name, None))

        # Show results
        self.console.print("\n[bold cyan]Results:[/bold cyan]\n")
        success_count = 0
        for name, result in results:
            if result:
                self.console.print(f"[green]✅ {name}[/green]")
                success_count += 1
            else:
                self.console.print(f"[red]❌ {name}[/red]")

        self.console.print(
            f"\n[bold]Processed {success_count}/{len(urls)} URLs successfully[/bold]"
        )

    def view_settings(self) -> None:
        """Display current configuration."""
        self.console.print("\n[bold cyan]Current Settings[/bold cyan]\n")

        settings_table = Table(show_header=False, padding=(0, 2))
        settings_table.add_row("[cyan]Download Directory[/cyan]", str(self.config.download_dir))
        settings_table.add_row("[cyan]Output Directory[/cyan]", str(self.config.output_dir))
        settings_table.add_row("[cyan]Max Concurrent Workers[/cyan]", str(self.config.max_workers))
        settings_table.add_row("[cyan]Request Timeout[/cyan]", f"{self.config.request_timeout}s")
        settings_table.add_row("[cyan]Rate Limit Delay[/cyan]", f"{self.config.request_delay}s")
        settings_table.add_row(
            "[cyan]Sketchfab Token[/cyan]",
            "[green]Set[/green]" if self.config.sketchfab_api_token else "[yellow]Not set[/yellow]",
        )
        settings_table.add_row("[cyan]Log Level[/cyan]", self.config.log_level)

        self.console.print(settings_table)
        self.console.print("\n[yellow]💡 Edit .env file to change settings[/yellow]\n")

    def run(self) -> None:
        """Run the TUI main loop."""
        self.print_header()

        while True:
            self.print_menu()
            choice = self.get_menu_choice()

            if choice == "1":
                self.wowhead_scraper_menu()
            elif choice == "2":
                self.sketchfab_scraper_menu()
            elif choice == "3":
                self.batch_processor_menu()
            elif choice == "4":
                self.view_settings()
            elif choice == "5":
                self.console.print(
                    "\n[bold cyan]👋 Thanks for using 3D Model Scraper![/bold cyan]\n"
                )
                break

            # Pause before next menu
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            self.console.clear()
            self.print_header()
