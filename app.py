import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

st.set_page_config(
    page_title="TakeMeter",
    page_icon="✈️",
    layout="centered"
)

LABEL_MAP = {"vague": 0, "partial": 1, "detailed": 2}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

LABEL_FEEDBACK = {
    "vague": {
        "emoji": "🔴",
        "title": "Too Vague",
        "feedback": "Your post is missing key details. Try adding a specific destination, travel dates, budget, and your interests.",
        "tip": "Instead of 'Where should I go this summer?' try 'I am planning a 2-week solo trip to Japan in August with a $2,000 budget. I love street food and temples.'"
    },
    "partial": {
        "emoji": "🟡",
        "title": "Partially Detailed",
        "feedback": "Good start! Adding your budget, specific interests, or travel style will help others give you more targeted advice.",
        "tip": "Try adding details like your budget, whether you prefer adventure or relaxation, group size, or any specific needs."
    },
    "detailed": {
        "emoji": "🟢",
        "title": "Well Detailed",
        "feedback": "Great post! You have provided enough detail for others to give you fully personalized advice.",
        "tip": "Your post includes a destination, context details, and personalization information. Responders can help you immediately."
    }
}

@st.cache_resource
def load_model():
    model_name = "dan0103/takemeter"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    return tokenizer, model

def classify_post(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    pred_id = torch.argmax(probs).item()
    pred_label = ID_TO_LABEL[pred_id]
    confidence = probs[pred_id].item()
    all_probs = {ID_TO_LABEL[i]: probs[i].item() for i in range(len(ID_TO_LABEL))}
    return pred_label, confidence, all_probs

# Header
st.title("✈️ TakeMeter")
st.markdown("Paste your r/travel post below to find out how detailed it is.")
st.divider()

# Load model outside spinner
tokenizer, model = load_model()

# Input
st.subheader("Your r/travel Post")
post_text = st.text_area(
    label="post",
    placeholder="e.g. I am planning a 2-week trip to Japan in April with my partner. Budget is $4,000. We love food, temples, and avoiding tourist crowds. Any recommendations?",
    height=160,
    label_visibility="collapsed"
)

# Classify button
if st.button("Classify Post", type="primary"):
    if not post_text.strip():
        st.warning("Please enter a post before classifying.")
    else:
        label, confidence, all_probs = classify_post(post_text, tokenizer, model)
        feedback = LABEL_FEEDBACK[label]

        st.divider()

        # Result
        st.subheader("Result")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Classification", f"{feedback['emoji']} {feedback['title']}")
        with col2:
            st.metric("Confidence", f"{confidence:.0%}")

        st.info(feedback["feedback"])
        st.caption(f"💡 {feedback['tip']}")

        st.divider()

        # Confidence breakdown
        st.subheader("Confidence Breakdown")
        for lbl in ["vague", "partial", "detailed"]:
            prob = all_probs[lbl]
            emoji = LABEL_FEEDBACK[lbl]["emoji"]
            st.markdown(f"{emoji} **{lbl}** — {prob:.0%}")
            st.progress(prob)

# Footer
st.divider()
st.caption("TakeMeter · AI201 Project 3 · Fine-tuned DistilBERT on r/travel posts")
