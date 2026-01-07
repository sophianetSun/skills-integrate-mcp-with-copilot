# Integrate MCP with Copilot

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey sophianetSun!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/sophianetSun/skills-integrate-mcp-with-copilot/issues/1)

---

## Running locally (with persistence)

1. Install dependencies: `pip install -r requirements.txt`
2. Optionally set a custom database location: `export DB_PATH="sqlite:///./data.db"`
	- Defaults to a local SQLite file; `.gitignore` already excludes `*.sqlite`.
3. Start the API: `uvicorn src.app:app --reload`
	- Tables are created on startup and seeded once with the sample activities.

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

