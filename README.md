# SQLGenieAgent

SQLGenieAgent is a powerful tool that bridges the gap between natural language and SQL queries. It allows users to input natural language prompts and generates SQL queries based on the provided database schema. SQLGenieAgent leverages a hybrid approach combining rule-based systems and large language models (LLMs) for flexibility, accuracy, and cost-effectiveness.

---

## Features

- **Natural Language to SQL**: Converts user-friendly prompts into SQL queries.
- **Hybrid Approach**: Combines rule-based systems, OpenAI's GPT-3.5-turbo, and Google's FLAN-T5 for optimal performance.
- **Schema-Aware**: Understands database schemas to generate accurate queries.
- **Customizable**: Supports multiple configuration options for different use cases.
- **REST API**: Provides an endpoint for programmatic access to SQL generation.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Pip (Python package manager)
- (Optional) OpenAI API key for GPT-3.5-turbo integration

### Steps

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd SQLGenieAgent
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit the .env file to include your configuration
   ```

5. Run the application:

   ```bash
   python main.py
   ```

6. Access the application via a browser at `http://127.0.0.1:5000/`.

---


### Steps to Update the File
1. Open the `README.md` file in your editor.
2. Replace its content with the updated content above.
3. Save the file.

### Commit the Changes
Run the following commands to commit the updated `README.md`:

```bash
git add README.md
git commit -m "Add detailed installation steps and improve README.md formatting"
git push origin <branch-name>

