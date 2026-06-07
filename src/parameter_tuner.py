"""Parameter tuning UI for the 3D model scraper."""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, FloatPrompt, Prompt
from rich.table import Table
from rich.text import Text

from .config import Config, get_config


@dataclass
class ParameterProfile:
    """A profile containing tuned parameters for specific use cases."""
    
    name: str
    description: str
    max_workers: int
    request_timeout: int
    request_delay: float
    download_dir: str
    output_dir: str
    log_level: str
    wowhead_headless: bool
    wowhead_timeout: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParameterProfile":
        """Create profile from dictionary."""
        return cls(**data)


class ParameterTuner:
    """Interactive UI for tuning scraper parameters."""
    
    # Predefined profiles for common use cases
    PROFILES = {
        "fast": ParameterProfile(
            name="Fast Mode",
            description="High concurrency, low timeouts - for rapid batch processing",
            max_workers=8,
            request_timeout=15,
            request_delay=0.5,
            download_dir="./downloads",
            output_dir="./outputs",
            log_level="WARNING",
            wowhead_headless=True,
            wowhead_timeout=15000,
        ),
        "balanced": ParameterProfile(
            name="Balanced Mode",
            description="Moderate settings - good for general use",
            max_workers=4,
            request_timeout=30,
            request_delay=1.0,
            download_dir="./downloads",
            output_dir="./outputs",
            log_level="INFO",
            wowhead_headless=True,
            wowhead_timeout=30000,
        ),
        "reliable": ParameterProfile(
            name="Reliable Mode",
            description="Conservative settings - prioritizes stability over speed",
            max_workers=2,
            request_timeout=60,
            request_delay=2.0,
            download_dir="./downloads",
            output_dir="./outputs",
            log_level="DEBUG",
            wowhead_headless=True,
            wowhead_timeout=60000,
        ),
        "sketchfab": ParameterProfile(
            name="Sketchfab Optimized",
            description="Tuned for Sketchfab API with respect to rate limits",
            max_workers=3,
            request_timeout=30,
            request_delay=1.5,
            download_dir="./downloads/sketchfab",
            output_dir="./outputs/sketchfab",
            log_level="INFO",
            wowhead_headless=True,
            wowhead_timeout=30000,
        ),
        "wowhead": ParameterProfile(
            name="WoWHead Optimized",
            description="Tuned for WoWHead browser automation",
            max_workers=1,
            request_timeout=45,
            request_delay=1.0,
            download_dir="./downloads/wowhead",
            output_dir="./outputs/wowhead",
            log_level="INFO",
            wowhead_headless=True,
            wowhead_timeout=45000,
        ),
    }
    
    def __init__(self):
        """Initialize parameter tuner."""
        self.console = Console()
        self.config = get_config()
        self.custom_profiles: Dict[str, ParameterProfile] = {}
    
    def print_header(self) -> None:
        """Print tuner header."""
        self.console.print(
            Panel(
                "[bold cyan]⚙️  Parameter Tuning Interface[/bold cyan]\n"
                "[dim]Fine-tune scraper performance and behavior[/dim]",
                style="cyan",
            )
        )
    
    def show_quick_profiles(self) -> None:
        """Display available quick profiles."""
        self.console.print("\n[bold cyan]Available Quick Profiles:[/bold cyan]\n")
        
        profiles_table = Table(title="Quick Start Profiles", show_header=True)
        profiles_table.add_column("Profile", style="cyan")
        profiles_table.add_column("Description", style="green")
        profiles_table.add_column("Workers", style="yellow", justify="right")
        profiles_table.add_column("Delay (s)", style="yellow", justify="right")
        
        for key, profile in self.PROFILES.items():
            profiles_table.add_row(
                f"[bold]{key}[/bold]",
                profile.description,
                str(profile.max_workers),
                f"{profile.request_delay:.1f}",
            )
        
        self.console.print(profiles_table)
    
    def display_current_parameters(self) -> None:
        """Display current configuration parameters."""
        self.console.print("\n[bold cyan]Current Parameters:[/bold cyan]\n")
        
        params_table = Table(show_header=False, padding=(0, 2))
        params_table.add_column("Parameter", style="cyan")
        params_table.add_column("Value", style="green")
        
        # Download settings
        params_table.add_row("[bold]Download Settings[/bold]", "")
        params_table.add_row("  Download Directory", str(self.config.download_dir))
        params_table.add_row("  Output Directory", str(self.config.output_dir))
        params_table.add_row("  Max Concurrent Workers", str(self.config.max_workers))
        
        # Request settings
        params_table.add_row("[bold]Request Settings[/bold]", "")
        params_table.add_row("  Request Timeout", f"{self.config.request_timeout}s")
        params_table.add_row("  Rate Limit Delay", f"{self.config.request_delay}s")
        
        # WoWHead settings
        params_table.add_row("[bold]WoWHead Settings[/bold]", "")
        params_table.add_row("  Headless Mode", "✓ Yes" if self.config.wowhead_headless else "✗ No")
        params_table.add_row("  WoWHead Timeout", f"{self.config.wowhead_timeout}ms")
        
        # Logging
        params_table.add_row("[bold]Logging[/bold]", "")
        params_table.add_row("  Log Level", self.config.log_level)
        
        # API
        params_table.add_row("[bold]API[/bold]", "")
        token_status = "[green]Set[/green]" if self.config.sketchfab_api_token else "[yellow]Not set[/yellow]"
        params_table.add_row("  Sketchfab API Token", token_status)
        
        self.console.print(params_table)
    
    def apply_profile(self, profile_key: str) -> bool:
        """Apply a predefined profile."""
        if profile_key not in self.PROFILES and profile_key not in self.custom_profiles:
            self.console.print(f"[red]❌ Profile '{profile_key}' not found[/red]")
            return False
        
        profile = self.PROFILES.get(profile_key) or self.custom_profiles[profile_key]
        
        self.console.print(f"\n[bold cyan]Applying '{profile.name}'...[/bold cyan]")
        self.console.print(f"[dim]{profile.description}[/dim]\n")
        
        # Show changes
        changes_table = Table(title="Parameter Changes", show_header=True)
        changes_table.add_column("Parameter")
        changes_table.add_column("Current")
        changes_table.add_column("New")
        
        params = profile.to_dict()
        for key, new_value in params.items():
            if key == "name" or key == "description":
                continue
            
            old_value = getattr(self.config, key, None)
            if old_value != new_value:
                changes_table.add_row(
                    key.replace("_", " ").title(),
                    str(old_value),
                    str(new_value),
                )
        
        self.console.print(changes_table)
        
        if not Confirm.ask("\n[cyan]Apply these changes?[/cyan]"):
            self.console.print("[yellow]Profile application cancelled[/yellow]")
            return False
        
        # Update config
        for key, value in params.items():
            if key not in ("name", "description"):
                setattr(self.config, key, value)
        
        self.console.print("[green]✅ Profile applied successfully![/green]")
        return True
    
    def tune_parameter(self, param_name: str) -> bool:
        """Interactively tune a single parameter."""
        param_name_lower = param_name.lower()
        
        if param_name_lower == "max_workers":
            current = self.config.max_workers
            self.console.print(f"\n[cyan]Current value: {current}[/cyan]")
            self.console.print("[dim]Recommended range: 1-32[/dim]")
            new_value = IntPrompt.ask("Enter new value", default=current)
            if 1 <= new_value <= 32:
                self.config.max_workers = new_value
                self.console.print(f"[green]✅ Set to {new_value}[/green]")
                return True
            else:
                self.console.print("[red]❌ Value must be between 1 and 32[/red]")
                return False
        
        elif param_name_lower == "request_timeout":
            current = self.config.request_timeout
            self.console.print(f"\n[cyan]Current value: {current}s[/cyan]")
            self.console.print("[dim]Recommended range: 10-120 seconds[/dim]")
            new_value = IntPrompt.ask("Enter new value (seconds)", default=current)
            if 10 <= new_value <= 120:
                self.config.request_timeout = new_value
                self.console.print(f"[green]✅ Set to {new_value}s[/green]")
                return True
            else:
                self.console.print("[red]❌ Value must be between 10 and 120 seconds[/red]")
                return False
        
        elif param_name_lower == "request_delay":
            current = self.config.request_delay
            self.console.print(f"\n[cyan]Current value: {current}s[/cyan]")
            self.console.print("[dim]Recommended range: 0.1-5.0 seconds[/dim]")
            new_value = FloatPrompt.ask("Enter new value (seconds)", default=current)
            if 0.1 <= new_value <= 5.0:
                self.config.request_delay = new_value
                self.console.print(f"[green]✅ Set to {new_value}s[/green]")
                return True
            else:
                self.console.print("[red]❌ Value must be between 0.1 and 5.0 seconds[/red]")
                return False
        
        elif param_name_lower == "wowhead_timeout":
            current = self.config.wowhead_timeout
            self.console.print(f"\n[cyan]Current value: {current}ms[/cyan]")
            self.console.print("[dim]Recommended range: 10000-120000 milliseconds[/dim]")
            new_value = IntPrompt.ask("Enter new value (milliseconds)", default=current)
            if 10000 <= new_value <= 120000:
                self.config.wowhead_timeout = new_value
                self.console.print(f"[green]✅ Set to {new_value}ms[/green]")
                return True
            else:
                self.console.print("[red]❌ Value must be between 10000 and 120000 ms[/red]")
                return False
        
        elif param_name_lower == "log_level":
            current = self.config.log_level
            self.console.print(f"\n[cyan]Current value: {current}[/cyan]")
            new_value = Prompt.ask(
                "Enter new level",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default=current,
            )
            self.config.log_level = new_value
            self.console.print(f"[green]✅ Set to {new_value}[/green]")
            return True
        
        elif param_name_lower == "download_dir":
            current = self.config.download_dir
            self.console.print(f"\n[cyan]Current value: {current}[/cyan]")
            new_value = Prompt.ask("Enter new directory path", default=current)
            self.config.download_dir = new_value
            Path(new_value).mkdir(parents=True, exist_ok=True)
            self.console.print(f"[green]✅ Set to {new_value}[/green]")
            return True
        
        elif param_name_lower == "output_dir":
            current = self.config.output_dir
            self.console.print(f"\n[cyan]Current value: {current}[/cyan]")
            new_value = Prompt.ask("Enter new directory path", default=current)
            self.config.output_dir = new_value
            Path(new_value).mkdir(parents=True, exist_ok=True)
            self.console.print(f"[green]✅ Set to {new_value}[/green]")
            return True
        
        elif param_name_lower == "wowhead_headless":
            current = self.config.wowhead_headless
            self.console.print(f"\n[cyan]Current value: {'Yes' if current else 'No'}[/cyan]")
            new_value = Confirm.ask("Enable headless mode?")
            self.config.wowhead_headless = new_value
            self.console.print(f"[green]✅ Set to {'Yes' if new_value else 'No'}[/green]")
            return True
        
        else:
            self.console.print(f"[red]❌ Unknown parameter: {param_name}[/red]")
            return False
    
    def show_custom_profile_menu(self) -> None:
        """Show menu for managing custom profiles."""
        while True:
            self.console.print("\n[bold cyan]Custom Profiles Menu[/bold cyan]\n")
            
            menu_table = Table(show_header=False)
            menu_table.add_row("1", "Create new profile")
            menu_table.add_row("2", "Load profile from current config")
            menu_table.add_row("3", "List custom profiles")
            menu_table.add_row("4", "Delete custom profile")
            menu_table.add_row("5", "Back to main menu")
            self.console.print(menu_table)
            
            choice = Prompt.ask("\n[cyan]Select option[/cyan]", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self._create_custom_profile()
            elif choice == "2":
                self._save_current_as_profile()
            elif choice == "3":
                self._list_custom_profiles()
            elif choice == "4":
                self._delete_custom_profile()
            elif choice == "5":
                break
    
    def _create_custom_profile(self) -> None:
        """Create a new custom profile."""
        self.console.print("\n[bold cyan]Create Custom Profile[/bold cyan]\n")
        
        name = Prompt.ask("[cyan]Profile name[/cyan]")
        description = Prompt.ask("[cyan]Profile description[/cyan]")
        
        profile = ParameterProfile(
            name=name,
            description=description,
            max_workers=IntPrompt.ask("Max workers", default=self.config.max_workers),
            request_timeout=IntPrompt.ask("Request timeout (s)", default=self.config.request_timeout),
            request_delay=FloatPrompt.ask("Request delay (s)", default=self.config.request_delay),
            download_dir=Prompt.ask("Download directory", default=self.config.download_dir),
            output_dir=Prompt.ask("Output directory", default=self.config.output_dir),
            log_level=Prompt.ask(
                "Log level",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default=self.config.log_level,
            ),
            wowhead_headless=Confirm.ask("WoWHead headless mode", default=self.config.wowhead_headless),
            wowhead_timeout=IntPrompt.ask("WoWHead timeout (ms)", default=self.config.wowhead_timeout),
        )
        
        profile_key = name.lower().replace(" ", "_")
        self.custom_profiles[profile_key] = profile
        self.console.print(f"[green]✅ Profile '{name}' created![/green]")
    
    def _save_current_as_profile(self) -> None:
        """Save current configuration as a profile."""
        name = Prompt.ask("[cyan]Profile name[/cyan]")
        description = Prompt.ask("[cyan]Profile description[/cyan]")
        
        profile = ParameterProfile(
            name=name,
            description=description,
            max_workers=self.config.max_workers,
            request_timeout=self.config.request_timeout,
            request_delay=self.config.request_delay,
            download_dir=self.config.download_dir,
            output_dir=self.config.output_dir,
            log_level=self.config.log_level,
            wowhead_headless=self.config.wowhead_headless,
            wowhead_timeout=self.config.wowhead_timeout,
        )
        
        profile_key = name.lower().replace(" ", "_")
        self.custom_profiles[profile_key] = profile
        self.console.print(f"[green]✅ Saved current config as '{name}'![/green]")
    
    def _list_custom_profiles(self) -> None:
        """List all custom profiles."""
        if not self.custom_profiles:
            self.console.print("[yellow]No custom profiles created yet[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Custom Profiles:[/bold cyan]\n")
        
        profiles_table = Table(show_header=True)
        profiles_table.add_column("Name", style="cyan")
        profiles_table.add_column("Description", style="green")
        profiles_table.add_column("Workers", style="yellow", justify="right")
        
        for key, profile in self.custom_profiles.items():
            profiles_table.add_row(
                profile.name,
                profile.description,
                str(profile.max_workers),
            )
        
        self.console.print(profiles_table)
    
    def _delete_custom_profile(self) -> None:
        """Delete a custom profile."""
        if not self.custom_profiles:
            self.console.print("[yellow]No custom profiles to delete[/yellow]")
            return
        
        profile_names = list(self.custom_profiles.keys())
        
        self.console.print("\n[cyan]Select profile to delete:[/cyan]\n")
        for i, name in enumerate(profile_names, 1):
            self.console.print(f"  {i}. {self.custom_profiles[name].name}")
        
        choice = IntPrompt.ask("Enter number", default=1)
        if 1 <= choice <= len(profile_names):
            profile_key = profile_names[choice - 1]
            del self.custom_profiles[profile_key]
            self.console.print("[green]✅ Profile deleted![/green]")
        else:
            self.console.print("[red]❌ Invalid selection[/red]")
    
    def show_advanced_tuning_menu(self) -> None:
        """Show menu for advanced parameter tuning."""
        while True:
            self.console.print("\n[bold cyan]Advanced Parameter Tuning[/bold cyan]\n")
            
            menu_table = Table(show_header=False)
            menu_table.add_row("1", "Tune max workers")
            menu_table.add_row("2", "Tune request timeout")
            menu_table.add_row("3", "Tune request delay")
            menu_table.add_row("4", "Tune WoWHead timeout")
            menu_table.add_row("5", "Set log level")
            menu_table.add_row("6", "Set download directory")
            menu_table.add_row("7", "Set output directory")
            menu_table.add_row("8", "Toggle WoWHead headless mode")
            menu_table.add_row("9", "Back to main menu")
            self.console.print(menu_table)
            
            choice = Prompt.ask("\n[cyan]Select option[/cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            if choice == "1":
                self.tune_parameter("max_workers")
            elif choice == "2":
                self.tune_parameter("request_timeout")
            elif choice == "3":
                self.tune_parameter("request_delay")
            elif choice == "4":
                self.tune_parameter("wowhead_timeout")
            elif choice == "5":
                self.tune_parameter("log_level")
            elif choice == "6":
                self.tune_parameter("download_dir")
            elif choice == "7":
                self.tune_parameter("output_dir")
            elif choice == "8":
                self.tune_parameter("wowhead_headless")
            elif choice == "9":
                break
    
    def run(self) -> None:
        """Run the parameter tuning interface."""
        while True:
            self.console.clear()
            self.print_header()
            
            self.console.print("\n[bold cyan]Main Menu[/bold cyan]\n")
            
            menu_table = Table(show_header=False)
            menu_table.add_row("1", "View current parameters")
            menu_table.add_row("2", "Apply quick profile")
            menu_table.add_row("3", "Advanced tuning")
            menu_table.add_row("4", "Manage custom profiles")
            menu_table.add_row("5", "Show recommendations")
            menu_table.add_row("6", "Export parameters")
            menu_table.add_row("7", "Exit")
            self.console.print(menu_table)
            
            choice = Prompt.ask("\n[cyan]Select option[/cyan]", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                self.display_current_parameters()
            elif choice == "2":
                self.show_quick_profiles()
                profile_choice = Prompt.ask(
                    "\n[cyan]Enter profile name to apply (or press Enter to skip)[/cyan]",
                    default="",
                )
                if profile_choice:
                    self.apply_profile(profile_choice)
            elif choice == "3":
                self.show_advanced_tuning_menu()
            elif choice == "4":
                self.show_custom_profile_menu()
            elif choice == "5":
                self._show_recommendations()
            elif choice == "6":
                self._export_parameters()
            elif choice == "7":
                self.console.print("\n[bold cyan]👋 Thanks for using Parameter Tuner![/bold cyan]\n")
                break
            
            if choice != "7":
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def _show_recommendations(self) -> None:
        """Show tuning recommendations based on system analysis."""
        self.console.print("\n[bold cyan]Tuning Recommendations[/bold cyan]\n")
        
        recommendations = []
        
        # Analyze current settings
        if self.config.max_workers > 8:
            recommendations.append(
                ("[yellow]⚠️  High concurrency[/yellow]",
                 "Consider reducing max_workers if you experience rate limiting or memory issues")
            )
        
        if self.config.request_delay < 0.5:
            recommendations.append(
                ("[yellow]⚠️  Low request delay[/yellow]",
                 "Very aggressive rate limit. Ensure API permits this frequency")
            )
        
        if self.config.request_timeout < 15:
            recommendations.append(
                ("[yellow]⚠️  Short timeout[/yellow]",
                 "May cause failures on slow connections. Consider increasing")
            )
        
        if self.config.log_level == "DEBUG":
            recommendations.append(
                ("[blue]ℹ️  Debug logging[/blue]",
                 "Verbose logging enabled. This will impact performance")
            )
        
        if not recommendations:
            self.console.print("[green]✅ Configuration looks good![/green]")
        else:
            rec_table = Table(title="Recommendations", show_header=False)
            for issue, suggestion in recommendations:
                rec_table.add_row(issue, suggestion)
            self.console.print(rec_table)
    
    def _export_parameters(self) -> None:
        """Export current parameters to .env format."""
        self.console.print("\n[bold cyan]Export Parameters[/bold cyan]\n")
        
        export_path = Prompt.ask(
            "[cyan]Enter export path[/cyan]",
            default=".env.tuned",
        )
        
        try:
            env_content = (
                f"# Auto-generated by Parameter Tuner\n"
                f"DOWNLOAD_DIR={self.config.download_dir}\n"
                f"OUTPUT_DIR={self.config.output_dir}\n"
                f"MAX_WORKERS={self.config.max_workers}\n"
                f"REQUEST_TIMEOUT={self.config.request_timeout}\n"
                f"REQUEST_DELAY={self.config.request_delay}\n"
                f"WOWHEAD_HEADLESS={str(self.config.wowhead_headless).lower()}\n"
                f"WOWHEAD_TIMEOUT={self.config.wowhead_timeout}\n"
                f"LOG_LEVEL={self.config.log_level}\n"
            )
            
            with open(export_path, "w") as f:
                f.write(env_content)
            
            self.console.print(f"[green]✅ Parameters exported to {export_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]")
            logger.error(f"Parameter export failed: {e}")
