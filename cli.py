# cli.py

import typer
import requests
from typing import Optional

app = typer.Typer()


@app.command()
def get_user_projects(username: str):
    """
    Retrieve and display projects for a given GitHub username.
    """
    response = requests.get(f"http://localhost:8000/users/{username}/projects")
    if response.status_code == 200:
        projects = response.json()
        if projects:
            typer.echo(f"Projects for user '{username}':")
            for project in projects:
                typer.echo(f"- {project['name']}: {project['description']}")
                typer.echo(f"  Stars: {project['stars']}, Forks: {project['forks']}\n")
        else:
            typer.echo(f"No projects found for user '{username}'.")
    elif response.status_code == 404:
        typer.echo(f"User '{username}' not found.")
    else:
        typer.echo(f"Error: {response.json().get('detail', 'Unknown error')}")


@app.command()
def get_recent_users(n: int = typer.Argument(5, help="Number of recent users to retrieve")):
    """
    Retrieve and display the N most recent users saved in the database.
    """
    response = requests.get(f"http://localhost:8000/users/recent/{n}")
    if response.status_code == 200:
        users = response.json()
        if users:
            typer.echo(f"Most recent {n} users:")
            for user in users:
                typer.echo(f"- {user['username']} (ID: {user['id']})")
        else:
            typer.echo("No users found in the database.")
    else:
        typer.echo(f"Error: {response.json().get('detail', 'Unknown error')}")


@app.command()
def get_most_starred_projects(n: int = typer.Argument(5, help="Number of most starred projects to retrieve")):
    """
    Retrieve and display the N most starred projects saved in the database.
    """
    response = requests.get(f"http://localhost:8000/projects/most-starred/{n}")
    if response.status_code == 200:
        projects = response.json()
        if projects:
            typer.echo(f"Top {n} most starred projects:")
            for project in projects:
                typer.echo(f"- {project['name']} by User ID {project['user_id']}")
                typer.echo(f"  Stars: {project['stars']}, Forks: {project['forks']}\n")
        else:
            typer.echo("No projects found in the database.")
    else:
        typer.echo(f"Error: {response.json().get('detail', 'Unknown error')}")


if __name__ == "__main__":
    app()
