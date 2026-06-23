# TakeMeter

A fine-tuned text classifier that evaluates discourse quality in r/travel by measuring how much actionable detail a post provides to potential responders.

## Overview

TakeMeter classifies r/travel posts into three quality levels based on how much detail they provide:

| Label | Description |
|-------|-------------|
| `vague` | Too broad or missing too many details; a responder would need to ask multiple clarifying questions |
| `partial` | Names a specific destination with at least 2 context details but missing key personalization info |
| `detailed` | Specific destination plus 3 or more of: budget, interests, travel style, group size, or specific needs |

**Why this matters:** A well-detailed question attracts better, more personalized responses. TakeMeter can identify vague posts early and nudge users to add more details before posting — reducing repeated questions and improving advice quality in the community.

## Repository Structure
```
TakeMeter/
├── planning.md                  # Label design, data collection plan, evaluation metrics
└── README.md                    # This file
evaluation metrics
├── 200_reddit_post.csv          # Labeled dataset (200 examples)
├── confusion_matrix.png         # Fine-tuned model confusion matrix
├── evaluation_results.json      # Baseline vs. fine-tuned model metrics
```

---

## Dataset

**Source:** r/travel (public posts)

**Collection method:** 200 posts collected using two methods:
- 100 posts manually browsed and copy-pasted from r/travel
- 100 posts retrieved from r/travel via Perplexity AI and manually reviewed for label accuracy

**Label distribution:**

| Label | Count | % of Dataset |
|-------|-------|-------------|
| `vague` | 67 | 33.5% |
| `partial` | 67 | 33.5% |
| `detailed` | 66 | 33.0% |
| **Total** | **200** | **100%** |

**Labeling process:** Each post was labeled manually using the decision rules defined in planning.md. No AI tool was used to pre-assign labels. The dataset was split automatically by the notebook into train/validation/test sets (70% / 15% / 15%), resulting in 140 training, 30 validation, and 30 test examples.

**Difficult labeling cases:** Three posts required explicit decision rules:
- Posts naming a broad region (e.g., "Southeast Asia") without a specific country were labeled `vague` despite having some context details
- Posts with a travel style hint (e.g., "budget traveler") without a specific budget figure were labeled `partial` not `detailed`
- Country comparison posts (e.g., "Should I go to Thailand or Vietnam?") with no supporting context were labeled `vague`

---

## Model and Training

**Base model:** `distilbert-base-uncased` (HuggingFace)

DistilBERT is a smaller, faster version of BERT that retains 97% of its language understanding capability at 40% fewer parameters. It was chosen because it fine-tunes efficiently on small datasets and runs comfortably on a free T4 GPU in Google Colab.

**Training setup:**
- Platform: Google Colab (T4 GPU)
- Framework: HuggingFace Transformers + Datasets
- Training time: approximately 1 minute on T4 GPU

**Hyperparameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Epochs | 3 | Appropriate for 200 examples; more risks overfitting |
| Learning rate | 2e-5 | Standard starting point for fine-tuning BERT-family models |
| Batch size | 16 | Fits T4 GPU memory comfortably |
| Max sequence length | 256 | Sufficient for r/travel post lengths |
| Weight decay | 0.01 | Light regularization to reduce overfitting on small dataset |

**Training curve:**

| Epoch | Training Loss | Validation Loss | Accuracy |
|-------|--------------|-----------------|----------|
| 1 | No log | 1.096 | 0.400 |
| 2 | 1.114 | 1.060 | 0.600 |
| 3 | 1.082 | 0.985 | 0.833 |

The model improved consistently across all 3 epochs with validation loss decreasing and accuracy climbing, indicating healthy training behavior with no signs of overfitting.

---

## Evaluation Report

### Overall Results

| Model | Accuracy |
|-------|----------|
| Zero-shot baseline (Groq llama-3.3-70b-versatile) | 1.000 |
| Fine-tuned DistilBERT | 0.867 |

The fine-tuned model performed 13.3% below the zero-shot baseline. This is addressed in the reflection section below.

### Per-Class Metrics

**Zero-shot baseline (Groq):**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| `vague` | 1.00 | 1.00 | 1.00 |
| `partial` | 1.00 | 1.00 | 1.00 |
| `detailed` | 1.00 | 1.00 | 1.00 |
| **macro avg** | **1.00** | **1.00** | **1.00** |

**Fine-tuned DistilBERT:**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| `vague` | 1.00 | 0.80 | 0.89 |
| `partial` | 0.77 | 1.00 | 0.87 |
| `detailed` | 0.89 | 0.80 | 0.84 |
| **macro avg** | **0.89** | **0.87** | **0.87** |

### Confusion Matrix (Fine-Tuned Model)

| True \ Predicted | `vague` | `partial` | `detailed` |
|-----------------|---------|-----------|------------|
| **`vague`** | 8 | 1 | 1 |
| **`partial`** | 0 | 10 | 0 |
| **`detailed`** | 0 | 2 | 8 |

The model never confuses `vague` and `detailed` directly. All errors involve adjacent label boundaries. The most common error direction is `detailed` predicted as `partial`, suggesting the model sometimes underestimates post quality.

![Confusion Matrix](./evaluation%20metrics/confusionn%20matrix.png)

### Success Criteria Assessment

| Criteria | Target | Result | Status |
|----------|--------|--------|--------|
| Overall accuracy | >= 80% | 86.7% | ✅ |
| F1 for `vague` | >= 0.80 | 0.89 | ✅ |
| F1 for `detailed` | >= 0.80 | 0.84 | ✅ |
| F1 for `partial` | >= 0.65 | 0.87 | ✅ |

All four success criteria were met.

### Sample Classifications

The following examples were run through the fine-tuned model:

| Post (truncated) | True Label | Predicted | Confidence |
|------------------|------------|-----------|------------|
| "Any good travel recommendations for this summer?" | `vague` | `vague` | high |
| "I'm visiting Japan for 2 weeks in April, what are the must-see places?" | `partial` | `partial` | high |
| "Planning a 10-day trip to Italy in September with my partner. Budget is $3,000. We love food, history, and avoiding tourist crowds." | `detailed` | `detailed` | high |
| "Is Southeast Asia still worth visiting with all the tourism now?" | `vague` | `partial` | 0.35 |
| "First time in Southeast Asia - 3 weeks in January. Budget $2,500, solo female traveler in my late 20s." | `detailed` | `partial` | 0.36 |

The `detailed` Italy post was correctly classified because it includes a specific destination (Rome), duration (10 days), travel month (September), budget ($3,000), interests (food, history), and a specific constraint (avoiding tourist crowds), hitting all the criteria for the `detailed` label decisively.

### Error Analysis

The fine-tuned model made 4 errors out of 30 test examples. All errors involved `partial` as either the predicted or true label, confirming it is the hardest boundary to learn.

**Error 1 — `detailed` predicted as `partial` (confidence: 0.36)**
*"First time in Southeast Asia - 3 weeks in January. Budget $2,500, solo female traveler in my late 20s. I'm interested in food, culture, and a bit of nature. Want to avoid full party scenes."*
The post mentions "Southeast Asia," a broad region rather than a specific country. By our decision rules, broad regions push toward `vague`. The model may have picked up on this regional breadth and pulled the prediction toward `partial` rather than `detailed`. The low confidence (0.36) confirms the model was genuinely uncertain.

**Error 2 — `detailed` predicted as `partial` (confidence: 0.37)**
*"Family trip to Costa Rica for 12 days in July - 2 adults, 3 kids ages 6-12. Budget $6,000 from Atlanta. We want zip-lining, wildlife, beaches, and volcano experiences."*
This is a clearly detailed post with specific destination, duration, month, group composition, budget, and interests. The low confidence (0.37) suggests the model was uncertain. The post may have been truncated during tokenization, causing the model to miss some of the detail signals toward the end.

**Error 3 — `vague` predicted as `partial` (confidence: 0.35)**
*"Is Southeast Asia still worth visiting with all the tourism now?"*
This is an opinion or discussion post rather than a trip planning question. It does not fit cleanly into any label. The model picked up "Southeast Asia" as a destination signal and predicted `partial`. This reveals a gap in the label taxonomy: opinion posts were not explicitly addressed in the decision rules.

**Error 4 — `vague` predicted as `detailed` (confidence: 0.35)**
*"I want to travel somewhere I can disconnect from technology."*
This post expresses a specific interest (disconnecting from technology) without naming any destination. The model may have over-weighted the interest signal and predicted `detailed`. This is an edge case the taxonomy did not fully anticipate: a post with a clear interest but no destination.

### Reflection: What the Model Learned vs. What Was Intended

The model learned to classify posts reasonably well based on surface-level features: post length, presence of budget figures, destination specificity, and number of detail signals. This aligns closely with what was intended.

However, two gaps emerged between the intended label boundaries and what the model actually captured:

First, the model struggles with posts that express a specific interest or constraint without naming a destination. These posts share surface features with `detailed` posts (specific language, clear intent) but belong to `vague` by our definition. The model has not fully learned that a destination is a required anchor for any label above `vague`.

Second, the model over-predicts `partial` when uncertain. Since `partial` is the middle label, it shares features with both extremes. A short post with one detail looks partially like `vague`, and a long post missing one criterion looks partially like `detailed`. The model defaulted to `partial` in all ambiguous cases, which is a reasonable but imperfect heuristic.

The zero-shot baseline achieving 100% accuracy reveals that the label boundaries are learnable from surface patterns alone by a large language model. DistilBERT, being much smaller, approximates this but does not fully replicate it, particularly on edge cases that require deeper semantic understanding.

---

## Spec Reflection

**One way the spec helped guide implementation:**
The spec's emphasis on label design as the most important decision in the project was genuinely useful. The requirement to define explicit decision rules for edge cases before annotating any examples forced a level of precision that paid off during annotation. Having a written rule for the `vague` vs. `partial` boundary (broad region vs. specific country) made labeling consistent across all 200 examples and directly explains why the model learned the boundaries as cleanly as it did.

**One way implementation diverged from the spec:**
The spec anticipated that fine-tuning would outperform the zero-shot baseline, framing the baseline as "something to beat." In practice the opposite occurred: the zero-shot Groq baseline achieved 100% accuracy while the fine-tuned DistilBERT reached 86.7%. This was not a failure of the pipeline but a reflection of well-defined labels that a large language model can classify from surface patterns alone. The project diverged from the spec's implicit assumption by producing a case where the baseline was the stronger model, which turned out to be the most interesting finding to analyze.

---

## AI Usage

**1. Label taxonomy and dataset stress-testing (Claude)**
Claude was used throughout Milestone 1 to refine label definitions and decision rules through an iterative conversation. After the full 200-example dataset was collected, it was submitted to Claude for review. Claude identified 3 edge cases (posts #27, #44, #103) and caught formatting typos in posts #151, #163, and #165. No labels were changed without human judgment. Claude's suggestions were reviewed and accepted or rejected based on the decision rules already established.

**2. Failure analysis (Claude)**
After fine-tuning, all 4 wrong predictions were submitted to Claude for pattern analysis. Claude identified two systematic patterns: the model's tendency to over-predict `partial` when uncertain, and its difficulty with posts that express specific interests without naming a destination. These patterns were verified manually by re-reading each misclassified example before being included in this report.

**3. Data retrieval (Perplexity AI)**
Perplexity AI was used to retrieve 100 real r/travel posts matching each label's criteria. Perplexity retrieved actual Reddit posts rather than generating synthetic ones. Every retrieved post was manually reviewed and labeled by the human annotator before being included in the dataset.

---

## Getting Started

### Requirements
```
torch
transformers
datasets
scikit-learn
groq
pandas
numpy
matplotlib
```

### Running the Notebook
1. Open the TakeMeter Colab notebook
2. Set runtime to T4 GPU (Runtime > Change runtime type > T4 GPU)
3. Add your Groq API key to Colab Secrets as `GROQ_API_KEY`
4. Run all cells top to bottom
5. Upload `200_reddit_post.csv` when prompted in Section 1

### Running the Deployed Interface
After fine-tuning, a Streamlit interface is available for classifying new r/travel posts:
```bash
pip install streamlit
streamlit run app.py
```
Enter any r/travel post and the classifier will return the predicted label and confidence score.
