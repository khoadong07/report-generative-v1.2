"""
Script to seed interaction metrics into Excel data
- Comments: Calculated by counting ParentId references (real data)
- Reactions, Shares, Views: Fake random data for demo purposes
- Interactions: Calculated as Reactions + Shares + Comments
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys


def seed_interactions(input_file: str, output_file: str = None):
    """
    Add/update interaction columns:
    - Comments: Count of ParentId references (real data based on child rows)
    - Reactions, Shares: Random fake data (0-250)
    - Views: Random fake data (100-1000)
    - Interactions: Calculated as Reactions + Shares + Comments
    Only rows with Type ending in 'Topic' will have interaction metrics
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file (optional, defaults to input_demo.xlsx)
    """
    # Validate input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Set output file
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_demo{input_path.suffix}"
    
    print(f"📂 Reading: {input_file}")
    
    # Read Excel file
    try:
        df = pd.read_excel(input_file)
        print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        sys.exit(1)
    
    # Validate required columns
    required_cols = ["Type", "ParentId", "Id"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Error: Missing required columns: {', '.join(missing_cols)}")
        sys.exit(1)
    
    # Define interaction columns
    interaction_columns = ["Comments", "Reactions", "Shares", "Views", "Interactions"]
    
    # Check existing columns
    existing = [col for col in interaction_columns if col in df.columns]
    if existing:
        print(f"⚠️  Warning: {', '.join(existing)} already exist. They will be overwritten.")
    
    # Initialize all interaction columns with 0
    for col in interaction_columns:
        df[col] = 0
    
    # Identify Topic rows (Type ends with 'Topic')
    df['IsTopic'] = df['Type'].str.endswith('Topic', na=False)
    topic_count = df['IsTopic'].sum()
    print(f"📊 Found {topic_count} Topic rows out of {len(df)} total rows")
    
    print(f"✨ Calculating interaction metrics...")
    
    # 1. Comments = Count how many times each Id appears as ParentId (real data)
    print(f"   • Comments: Counting ParentId references...")
    parent_counts = df['ParentId'].value_counts().to_dict()
    
    for idx in df[df['IsTopic']].index:
        topic_id = df.at[idx, 'Id']
        df.at[idx, 'Comments'] = parent_counts.get(topic_id, 0)
    
    # 2. Reactions, Shares, Views, Interactions = Fake random data
    np.random.seed(42)  # For reproducibility
    
    print(f"   • Reactions, Shares, Views: Generating random values...")
    for idx in df[df['IsTopic']].index:
        df.at[idx, 'Reactions'] = np.random.randint(0, 251)
        df.at[idx, 'Shares'] = np.random.randint(0, 251)
        df.at[idx, 'Views'] = np.random.randint(100, 1001)  # Views typically higher
    
    # 3. Interactions = Sum of Reactions + Shares + Comments (calculated after Comments)
    print(f"   • Interactions: Calculating as Reactions + Shares + Comments...")
    df['Interactions'] = df['Reactions'] + df['Shares'] + df['Comments']
    
    # Calculate statistics for Topic rows only
    topic_df = df[df['IsTopic']]
    print(f"\n📈 Statistics for Topic rows:")
    print(f"   • Comments: Min={topic_df['Comments'].min()}, Max={topic_df['Comments'].max()}, Mean={topic_df['Comments'].mean():.1f}")
    print(f"   • Reactions: Min={topic_df['Reactions'].min()}, Max={topic_df['Reactions'].max()}, Mean={topic_df['Reactions'].mean():.1f}")
    print(f"   • Shares: Min={topic_df['Shares'].min()}, Max={topic_df['Shares'].max()}, Mean={topic_df['Shares'].mean():.1f}")
    print(f"   • Views: Min={topic_df['Views'].min()}, Max={topic_df['Views'].max()}, Mean={topic_df['Views'].mean():.1f}")
    print(f"   • Interactions: Min={topic_df['Interactions'].min()}, Max={topic_df['Interactions'].max()}, Mean={topic_df['Interactions'].mean():.1f}")
    
    # Calculate total engagement (Reactions + Shares + Comments)
    df["TotalEngagement"] = df["Reactions"] + df["Shares"] + df["Comments"]
    
    # Recalculate topic_df after adding TotalEngagement
    topic_df = df[df['IsTopic']]
    print(f"   • TotalEngagement: Min={topic_df['TotalEngagement'].min()}, Max={topic_df['TotalEngagement'].max()}, Mean={topic_df['TotalEngagement'].mean():.1f}")
    
    # Drop temporary column
    df.drop('IsTopic', axis=1, inplace=True)
    
    # Save to output file
    print(f"💾 Saving to: {output_file}")
    try:
        df.to_excel(output_file, index=False)
        print(f"✅ Success! Demo file created: {output_file}")
    except Exception as e:
        print(f"❌ Error saving Excel file: {e}")
        sys.exit(1)
    
    # Show sample data
    print("\n📊 Sample data (first 5 Topic rows):")
    cols_to_show = ["Comments", "Reactions", "Shares", "Views", "Interactions", "TotalEngagement"]
    if "Title" in df.columns:
        cols_to_show.insert(0, "Title")
    if "Type" in df.columns:
        cols_to_show.insert(0, "Type")
    
    # Only show columns that exist and filter for Topic rows
    cols_to_show = [c for c in cols_to_show if c in df.columns]
    sample_df = df[df['Type'].str.endswith('Topic', na=False)][cols_to_show].head()
    print(sample_df)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add interaction metrics to Excel data for Topic types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seed_interactions.py input.xlsx
  python seed_interactions.py input.xlsx -o output_demo.xlsx
  python seed_interactions.py demo/bidv-092025.xlsx
  
Logic:
  - Only rows with Type ending in 'Topic' (e.g., fbUserTopic, newsTopic) will have interactions
  - Comments: Real count based on how many times the Topic's Id appears as ParentId
  - Reactions, Shares: Random values (0-250)
  - Views: Random values (100-1000)
  - Interactions: Calculated as Reactions + Shares + Comments
        """
    )
    parser.add_argument("input_file", help="Input Excel file path")
    parser.add_argument("-o", "--output", help="Output Excel file path (default: input_demo.xlsx)")
    
    args = parser.parse_args()
    
    seed_interactions(args.input_file, args.output)
