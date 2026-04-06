# Contributing to Lyzev Chess

Thank you for your interest in contributing to our community chess game!

## How to Play

The game is played directly through GitHub Issues. You don't need to make Pull Requests or edit source code to participate!

1. Go to the project's [Issues](https://github.com/Lyzev/Lyzev/issues).
2. Create a new Issue.
3. Use the title format `chess|<move>` (e.g., `chess|e2e4` for UCI notation).
4. Submit the issue.
5. Our GitHub Actions workflow will evaluate the move. If it's valid, the repository's main `README.md` will be updated with the changed board status and the issue will be closed with a successful status comment. If invalid, the workflow will comment with an error.

## Development

If you want to contribute to the engine or mechanics:
- Fork the repository.
- Ensure your changes follow PEP 8 and use type hinting.
- You can run tests using `pytest` if available.
- Submit a Pull Request.

Happy developing and playing!
