import subprocess
import re
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Add a Git submodule using SSH, treat it as a Django app, and decouple it"

    def add_arguments(self, parser):
        parser.add_argument(
            "repo_url", type=str, help="The SSH URL of the Git repository"
        )
        parser.add_argument(
            "app_name", type=str, help="The name of the Django app to create"
        )
        parser.add_argument(
            "--branch", type=str, help="Specify a branch to add the submodule from"
        )

    def handle(self, *args, **options):
        repo_url = options["repo_url"]
        app_name = options["app_name"]
        branch = options.get("branch")

        # Validate app_name
        if not re.match(r"^[\w-]+$", app_name):
            self.stderr.write(
                self.style.ERROR(
                    f"Invalid app_name '{app_name}'. It must contain only letters, numbers, underscores, and hyphens."
                )
            )
            return

        # Define the root directory and submodule path
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        submodule_path = root_dir / app_name

        self.stdout.write(self.style.SUCCESS(f"Root directory: {root_dir}"))

        try:
            # Checks if the directory is a Git repository
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=root_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            # Check if the submodule is already initialized
            try:
                _ = subprocess.run(
                    ["git", "submodule", "status", app_name],
                    cwd=root_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"Submodule '{app_name}' already exists. Updating instead of adding."
                    )
                )

                # Update the submodule
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive", app_name],
                    cwd=root_dir,
                    check=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Submodule '{app_name}' updated successfully.")
                )
            except subprocess.CalledProcessError:
                # Submodule does not exist, handle potential conflicts
                if submodule_path.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"The path '{submodule_path}' already exists. Cleaning up..."
                        )
                    )
                    self.clean_submodule(app_name, root_dir)

                self.stdout.write(
                    self.style.SUCCESS(f"Adding submodule '{app_name}'...")
                )
                add_command = ["git", "submodule", "add", "--force"]
                if branch:
                    add_command.extend(["-b", branch])
                add_command.extend([repo_url, app_name])
                subprocess.run(
                    add_command,
                    cwd=root_dir,
                    check=True,
                    text=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Submodule '{app_name}' added successfully.")
                )

                # Initialize and update the submodule
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive", app_name],
                    cwd=root_dir,
                    check=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Submodule initialized at {submodule_path}")
                )

                # Decouple the submodule
                self.stdout.write(
                    self.style.WARNING(
                        f"Decoupling submodule '{app_name}' into a regular directory..."
                    )
                )
                self.clean_submodule(app_name, root_dir)

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Git command failed:\n{e.stderr}"))

            # Additional checks for .gitmodules file
            gitmodules_path = root_dir / ".gitmodules"
            if gitmodules_path.exists():
                with open(gitmodules_path, "r") as f:
                    content = f.read()
                    if app_name in content:
                        self.stderr.write(
                            self.style.WARNING(
                                f"The submodule '{app_name}' is mentioned in .gitmodules but might be misconfigured."
                            )
                        )
                        self.stderr.write(
                            self.style.WARNING(
                                "You may need to manually edit .gitmodules or remove and re-add the submodule."
                            )
                        )
            else:
                self.stderr.write(
                    self.style.WARNING(
                        "The .gitmodules file was not found. Ensure your Git repository is set up correctly."
                    )
                )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))

    def clean_submodule(self, app_name, root_dir):
        """
        Decouple the submodule from the repository and turn it into a regular directory.
        """
        try:
            # Remove the submodule from Git index
            subprocess.run(
                ["git", "rm", "--cached", app_name],
                cwd=root_dir,
                check=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Removed submodule references for '{app_name}'.")
            )

            # Remove from .gitmodules
            subprocess.run(
                [
                    "git",
                    "config",
                    "--file",
                    ".gitmodules",
                    "--remove-section",
                    f"submodule.{app_name}",
                ],
                cwd=root_dir,
                check=True,
            )

            # Remove from .git/config
            subprocess.run(
                ["git", "config", "--remove-section", f"submodule.{app_name}"],
                cwd=root_dir,
                check=True,
            )

            # Remove the .git directory inside the submodule if it exists
            submodule_path = root_dir / app_name
            git_dir = submodule_path / ".git"
            if git_dir.exists() and git_dir.is_dir():
                subprocess.run(["rm", "-rf", str(git_dir)], check=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Removed the .git directory from '{submodule_path}'."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"No .git directory found in '{submodule_path}'."
                    )
                )

            # Remove the submodule from .git/modules
            modules_dir = root_dir / ".git" / "modules" / app_name
            if modules_dir.exists() and modules_dir.is_dir():
                subprocess.run(["rm", "-rf", str(modules_dir)], check=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Removed the submodule directory from '.git/modules/{app_name}'."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"No submodule directory found in '.git/modules/{app_name}'."
                    )
                )

            # If the directory exists but the submodule is being re-added, delete it
            if submodule_path.exists() and not git_dir.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Directory '{submodule_path}' exists but is not a submodule. Removing it to avoid conflicts..."
                    )
                )
                subprocess.run(["rm", "-rf", str(submodule_path)], check=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Removed the existing directory '{submodule_path}'."
                    )
                )

        except subprocess.CalledProcessError as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to clean up submodule '{app_name}': {e.stderr}"
                )
            )
