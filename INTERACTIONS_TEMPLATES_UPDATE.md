# Interactions Templates Update

## Summary
Created dedicated HTML templates for slides that display interaction metrics (Reactions, Shares, Comments) to provide better visual layout and data presentation.

## Changes Made

### 1. New HTML Templates Created

#### `html/slide4_interactions.html`
- **Purpose**: Display top sources with interaction metrics
- **Columns**: 6 columns
  1. STT (Row number)
  2. Nguồn (Source name)
  3. Tổng tương tác (Total engagement = R+S+C)
  4. Reactions
  5. Shares
  6. Comments
- **Layout**: Wider columns for interaction metrics, optimized spacing

#### `html/slide5_interactions.html`
- **Purpose**: Display top posts with interaction metrics
- **Columns**: 9 columns
  1. STT (Row number)
  2. Nội dung (Content - truncated to 50 chars)
  3. Ngày (Date)
  4. Kênh (Channel)
  5. Nguồn (Source)
  6. Reactions
  7. Shares
  8. Comments
  9. URL (Link)
- **Layout**: Compact content column to make room for R/S/C metrics

### 2. Updated `merge_slides.py`

#### `merge_slide04()` method
- Added template selection logic
- Uses `slide4_interactions.html` when `show_interactions=True` and individual metrics exist
- Falls back to `slide4.html` for regular mode

#### `merge_slide05()` method
- Added template selection logic
- Uses `slide5_interactions.html` when `show_interactions=True` and individual metrics exist
- Falls back to `slide5.html` for regular mode

#### `_generate_table_rows_slide04()` method
- Updated to generate different HTML based on template type
- Interactions template: 6-column layout with separate R/S/C columns
- Regular template: 3-column layout (STT, Source, Count)

#### `_generate_table_rows_slide05()` method
- Updated to accept `show_interactions` parameter
- Interactions template: 9-column layout with separate R/S/C columns
- Regular template: 6-column layout (STT, Content, Date, Channel, Source, URL)
- Adjusted content truncation based on template (50 chars for interactions, 70 for regular)

## Template Selection Logic

The system automatically chooses the correct template based on:
1. `show_interactions` flag from slide data
2. Presence of individual metric columns (reactions, shares, comments) in table_rows

```python
show_interactions = data.get("show_interactions", False)
has_individual_metrics = data["table_rows"] and "reactions" in data["table_rows"][0]

if show_interactions and has_individual_metrics:
    # Use interactions template
else:
    # Use regular template
```

## Slides Using Interactions

Only 3 slides support interaction metrics:
1. **Slide 1** (Overview) - Already had `slide1_interactions.html` ✓
2. **Slide 4** (Top Sources) - Now has `slide4_interactions.html` ✓
3. **Slide 5** (Top Posts) - Now has `slide5_interactions.html` ✓

## Data Flow

1. User enables "Hiển thị Interactions" toggle in Streamlit UI
2. `show_interactions=True` passed to orchestrator
3. Slide generators check for R/S/C columns in data
4. Slide data includes `show_interactions` flag
5. `merge_slides.py` selects appropriate template
6. Table row generator creates HTML matching template layout

## Important Notes

- **Tổng tương tác** is ALWAYS calculated as Reactions + Shares + Comments (never uses Interactions column)
- The Interactions column in Excel is ignored completely
- Templates maintain consistent styling with original designs
- All changes are backward compatible - regular mode still works without interactions
