# Screen Analysis Scripts

This directory contains various utility scripts for screen analysis and processing.

In terminal, should move to this directory first.

## Setting up Virtual Environment

1. Create a new virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running screen_labeling.py

This script allows you to label screens with their corresponding categories and components.

Usage:
```bash
# For regular labeling:
python screen_labeling.py main --save-to-db --max-sites <number>

# For labeling with fusion analysis:
python screen_labeling.py main1 --save-to-db --max-sites <number>

# For HTML-only analysis:
python screen_labeling.py main2 --save-to-db --max-sites <number>
```

Example:
```bash
# Regular analysis
python screen_labeling.py main --save-to-db --max-sites 5

# Analysis with fusion components
python screen_labeling.py main1 --save-to-db --max-sites 5

# HTML-only analysis (processes more sites)
python screen_labeling.py main2 --save-to-db --max-sites 100
```

Parameters:
- Command: Choose analysis mode
  - `main`: Regular screen analysis
  - `main1`: Analysis with fusion components
  - `main2`: HTML-only analysis
- `--save-to-db`: Whether to save results to database (default: True)
- `--max-sites`: Maximum number of sites to analyze
  - Use 0 or negative number for no limit
  - Default: 5 for main/main1, 100 for main2

## Running update_embeddings.py

This script updates or generates embedding vectors for analyses in the database.

Usage:
```bash
python update_embeddings.py --batch-size <number_or_all> --mode <mode>
```

Example:
```bash
# Update regular embeddings
python update_embeddings.py --batch-size 10 --mode regular

# Update fusion embeddings
python update_embeddings.py --batch-size all --mode fusion

# Update HTML analysis embeddings
python update_embeddings.py --batch-size 10 --mode html
```

Parameters:
- `--batch-size`: Number of records to process in each batch or 'all'
- `--mode`: Processing mode (choices: 'regular', 'fusion', 'html', default: 'regular')

## Running search_similar.py

This script searches for similar screens using embedding vectors.

Usage:
```bash
python search_similar.py "<query_text>" --mode <mode> --top-k <number>
```

Example:
```bash
# Search in regular analyses
python search_similar.py "landing page with hero section" --mode regular --top-k 5

# Search in fusion analyses
python search_similar.py "checkout page with payment form" --mode fusion --top-k 3

# Search in HTML analyses
python search_similar.py "booking website" --mode html --top-k 10
```

Parameters:
- `query`: Search query text (required)
- `--mode`: Search mode (choices: 'regular', 'fusion', 'html', default: 'regular')
- `--top-k`: Number of top results to return (default: 5)

## Environment Variables

Make sure to configure the following variables in your `.env` file:
- `PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Google Gemini API key

## Note
- Always activate the virtual environment before running any scripts
- Ensure all required environment variables are set in `.env`
- The virtual environment directory (`venv/`) is gitignored
- Different analysis modes store results in separate tables:
  - Regular: screen_analysis
  - Fusion: screen_analysis_fusion
  - HTML: screen_html_analysis
