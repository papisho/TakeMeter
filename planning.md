# TakeMeter — Project Planning
## AI201 · Project 3

---

## 1. Community

**Chosen community:** r/travel

I chose r/travel because I personally enjoy traveling and frequently use this subreddit to look for advice. It stood out as the right choice due to its broad topic coverage, large and active member base, and the wide variety in post quality from highly detailed trip-planning questions to vague one-liners. These qualities make it ideal for a classification task.

Classifying post quality is genuinely useful for this community because a well-detailed question tends to attract better, more personalized responses. If a classifier can identify vague posts early, it could nudge users to add more details before posting reducing repeated questions and improving the overall quality of advice exchanged in the community.

---

## 2. Labels

I defined 3 labels that capture meaningful distinctions in post quality on r/travel:

### `vague` (0)
The post is too broad or missing too many details to give any targeted advice. A responder would need to ask multiple clarifying questions before providing any useful recommendations.

- **Example 1:** *"I want to travel, any good recommendations?"*
- **Example 2:** *"What's the best country to visit in summer?"*

### `partial` (1)
The post names a specific destination and includes at least 2 context details (e.g., duration, month, group size) but is missing key personalization information like budget, interests, or travel style. A responder can give some useful advice without asking clarifying questions first.

- **Example 1:** *"I want to travel to Africa for a month and visit 3 countries, any recommendations on where I should go?"*
- **Example 2:** *"I'm visiting Japan for 2 weeks in April, what are the must-see places?"*

### `detailed` (2)
The post includes a specific destination plus 3 or more of the following: budget, interests, travel style, group size, or specific needs. A responder can give fully personalized advice immediately.

- **Example 1:** *"I want to travel to Africa for a month and visit 3 countries. I have a budget of $4,000. I'm a solo traveler interested in ancient/cultural places and wildlife."*
- **Example 2:** *"Planning a 10-day trip to Italy in September with my partner. Budget is $3,000. We love food, history, and avoiding tourist crowds. We'll be based in Rome, what day trips and restaurants would you recommend?"*

---

## 3. Hard Edge Cases

### Edge Case 1: Broad region vs. specific destination (`vague` vs. `partial` boundary)

**Example post:** *"I'm going to Europe for 2 weeks this summer, any must-see places?"*

This post has a timeframe (2 weeks) and season (summer) but names a continent rather than a specific country or city. It could seem like `partial` because it has some details, but it is missing too many specifics to give personalized advice.

**Decision rule:** If the post names a broad region or continent rather than a specific country or city, AND is missing 2+ key details (budget, interests, travel style, group size), label it `vague`. The test is: *would a helpful responder need to ask multiple clarifying questions before giving any useful advice?* If yes → `vague`.

### Edge Case 2: Specific city with minimal context (`partial` vs. `detailed` boundary)

**Example post:** *"I'm visiting Paris for 5 days in June, what should I do?"*

This post names a specific city and includes duration and month, but is missing budget, interests, travel style, and group size.

**Decision rule:** If the post names a specific city/country with at least 2 context details, label it `partial` even if personalization details are missing. The test is: *can a responder give some useful recommendations without asking clarifying questions first?* If yes → at least `partial`. If the post also includes 3+ personalization details → `detailed`.

### Edge Case 3: Travel style hint without explicit budget (`partial` vs. `detailed` boundary)

**Example post:** *"Visiting South Africa for 3 weeks in October, 2 adults. Budget traveler, where to focus?"*

This post has a specific country, duration, month, group size, and a travel style hint ("budget traveler") but no actual budget figure.

**Decision rule:** A vague travel style label (e.g., "budget traveler") without a specific budget figure does not count as a full personalization detail. This post is labeled `partial` because the hint is insufficient for fully personalized advice.

### Edge Case 4: Country comparison posts (`vague` boundary)

**Example posts:**
- *"Should I go to Thailand or Vietnam?"*
- *"Is it better to visit Japan or South Korea?"*

These name specific countries but provide no duration, budget, interests, or timing.

**Decision rule:** A country comparison without any supporting context details is labeled `vague` a responder would still need to ask multiple clarifying questions before giving useful advice.

---

## 4. Data Collection Plan

Data was collected exclusively from r/travel, using public posts and questions from the subreddit. A total of 200 examples were collected using a combination of two methods:

- **Manual collection (100 examples):** Posts were manually browsed and copy-pasted from r/travel into a spreadsheet by randomly browsing the subreddit to ensure natural variety in post quality and topic coverage.
- **AI-assisted collection (100 examples):** Perplexity AI was used to retrieve real posts from r/travel matching each label's criteria. Every retrieved post was reviewed manually to confirm it matched the label definitions before being included in the dataset.

**Target distribution:** ~67 examples per label (~33% each) to ensure no class imbalance.

**Actual distribution achieved:**

| Label | Count | % of Dataset |
|-------|-------|-------------|
| `vague` (0) | 67 | 33.5% |
| `partial` (1) | 67 | 33.5% |
| `detailed` (2) | 66 | 33.0% |
| **Total** | **200** | **100%** |

No underrepresentation issues were encountered. All three labels were equally achievable from the source material.

**Contingency plan:** If any label had fallen below 20% after 200 examples, additional targeted collection would have focused specifically on that label; for example, searching r/travel for highly upvoted detailed trip-planning posts to boost the `detailed` category.

---

## 5. Evaluation Metrics

The following metrics will be used to evaluate both the fine-tuned model and the zero-shot baseline on the same test set:

### Overall Accuracy
The fraction of test examples correctly labeled across all three classes. This gives a high-level view of model performance but is insufficient on its own; it can mask situations where the model performs well on one label but fails on another.

### Per-class F1 Score
Since all three labels matter equally, F1 score (the harmonic mean of precision and recall) will be reported for each label individually. This captures both how often the model is correct when it predicts a label (precision) and how often it catches all true examples of that label (recall). A model that scores well on overall accuracy but has a near-zero F1 on `partial` or `detailed` would not be considered successful.

### Macro-averaged F1
The unweighted average of F1 across all three classes. Since the dataset is balanced (~33% per label), macro F1 is the single most informative summary metric, it treats all three labels equally regardless of their frequency.

### Confusion Matrix
A 3×3 matrix showing which labels the model confuses and in which direction. This is especially important for catching the most costly error type: classifying a `detailed` post as `vague`, which would incorrectly flag a high-quality, actionable question as unhelpful.

Accuracy alone is insufficient for this task because the three labels represent an ordered quality scale. Directional errors (e.g., `detailed` → `vague`) are more misleading than adjacent ones (e.g., `detailed` → `partial`), and per-class F1 with a confusion matrix makes these patterns visible.

---

## 6. Definition of Success

This classifier will be considered genuinely useful if it meets the following specific criteria on the held-out test set:

**Primary threshold:**
- Overall accuracy ≥ 80% on the test set for the fine-tuned model

**Per-class thresholds:**
- F1 ≥ 0.80 for `vague` — the model must reliably catch low-quality posts that would waste a responder's time
- F1 ≥ 0.80 for `detailed` — the model must reliably recognize high-quality, actionable posts without downgrading them
- F1 ≥ 0.65 for `partial` — a slightly lower threshold is acceptable here since `partial` sits between the two extremes and is the hardest boundary to learn; some confusion with adjacent labels is expected

**Baseline comparison:**
- The fine-tuned model must meaningfully outperform the zero-shot Groq baseline — a minimum improvement of 10 percentage points in overall accuracy would demonstrate that fine-tuning added real value

**Deployment standard:**
- If all three thresholds above are met, the classifier would be suitable for deployment in a real community tool; for example, a bot that nudges r/travel users to add more detail to their posts before submitting

A result above 95% accuracy would be treated with suspicion and investigated for test set leakage or labels that are too easy rather than accepted at face value.

---

## 7. AI Tool Plan

### Label stress-testing
Claude was used to stress-test the label taxonomy and dataset. After collecting and labeling all 200 examples, the full dataset was submitted to Claude for review. Claude identified 3 potential edge cases (posts #27, #44, and #103) and caught formatting typos in posts #151, #163, and #165 ("cras" → "crafts", "cra beer" → "craft beer"). The label definitions were also refined through an iterative conversation with Claude during Milestone 1, where edge case decision rules were tested against ambiguous example posts before any annotation began.

### Annotation assistance
No AI tool was used to pre-label examples before manual review. All 200 labels were assigned by the human annotator. Perplexity AI was used solely for data retrieval, to find real r/travel posts matching each label's criteria not for labeling. After collection was complete, Claude reviewed the full dataset for consistency, but no labels were changed based on AI suggestion without human judgment.

### Failure analysis
After fine-tuning, the list of misclassified test examples will be submitted to Claude with the following prompt: *"Here are posts my classifier got wrong. Can you identify any common patterns similar post length, specific label pairs being confused, ambiguous language, or structural features that might explain the errors?"* The patterns Claude identifies will then be verified manually by re-reading the misclassified examples before being included in the evaluation report.

---

## 8. Stretch Feature Plan

**Chosen stretch feature: Deployed Interface**

A simple web interface will be built after fine-tuning that accepts a new r/travel post as input, runs it through the fine-tuned DistilBERT classifier, and displays the predicted label (`vague`, `partial`, or `detailed`) along with a confidence score. The interface will be built using Streamlit or Flask and committed to the GitHub repository with instructions on how to run it locally documented in the README.
