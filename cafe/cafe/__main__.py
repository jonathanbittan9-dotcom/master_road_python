import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.web.routes import app


def main():
    app.run(debug=True , port = 3000)


if __name__ == "__main__":
    main()
