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

## Deactivating Virtual Environment

When you're done working with the scripts, you can deactivate the virtual environment:
```bash
deactivate
```

## Running screen_labeling.py

This script allows you to label screens with their corresponding categories and components.

Usage:
```bash
# For regular labeling:
python screen_labeling.py main --save-to-db --max-sites <number>

# For labeling with fusion analysis:
python screen_labeling.py main1 --save-to-db --max-sites <number>
```

Example:
```bash
# Regular analysis
python screen_labeling.py main --save-to-db --max-sites 5

# Analysis with fusion components
python screen_labeling.py main1 --save-to-db --max-sites 5
```

Parameters:
- Command: Choose analysis mode
  - `main`: Regular screen analysis
  - `main1`: Analysis with fusion components
- `--save-to-db`: Whether to save results to database (default: True)
- `--max-sites`: Maximum number of sites to analyze (default: 5)

The script will:
1. Load images from the database
2. For regular analysis (main):
   - Process web content and images separately
   - Generate basic component and category labels
3. For fusion analysis (main1):
   - Process web content and images
   - Combine analyses using fusion analyzer
   - Generate enhanced component labels
4. Save results to appropriate database table
   - Regular analysis: 'screen_analysis' table
   - Fusion analysis: 'screen_analysis_fusion' table

## Running search_similar.py

This script helps find similar screens based on embedding vectors.

Usage:
```bash
python search_similar.py --query <query_image> --top_k <num_results> [--threshold <similarity_threshold>]
```

Example:
```bash
python search_similar.py --query ./screens/homepage.jpg --top_k 5 --threshold 0.8
```

Parameters:
- `query`: Path to the query image
- `top_k`: Number of similar results to return
- `threshold`: (Optional) Minimum similarity score threshold

## Running update_embeddings.py

This script updates or generates embedding vectors for all screens in the database.

Usage:
```bash
python update_embeddings.py --batch_size <batch_size> [--force]
```

Example:
```bash
python update_embeddings.py --batch_size 32 --force
```

Parameters:
- `batch_size`: Number of images to process in each batch
- `force`: (Optional) Force update existing embeddings

The script will:
1. Load screen images from the database
2. Generate embedding vectors using the embedding processor
3. Update the database with new vectors
4. Show progress and completion summary

## Environment Variables

Make sure to configure the following variables in your `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection string
- `MODEL_NAME`: Name of the embedding model to use

## Note
- Always activate the virtual environment before running any scripts
- Ensure all required environment variables are set in `.env`
- The virtual environment directory (`venv/`) is gitignored
