import streamlit as st

# ---- Tunable coefficients (all in one place) ----
STEPS_W = 0.0005       # was 0.02   → now 0.5 points per 1000 steps
MODERATE_W = 0.10      # was 0.15   → 30 min ≈ 3 points
VIGOROUS_W = 0.30      # was 0.35   → 10 min ≈ 3 points
SLEEP_HOURS_W = 3.0    # unchanged  → per hour above/below 7 h
SLEEP_QUALITY_W = 0.15 # unchanged
HR_STRESS_W = 0.9      # unchanged

def compute_body_battery(
    sleep_hours: float,
    sleep_quality: int,
    steps: int,
    moderate_min: int,
    vigorous_min: int,
    rhr: int,
    rhr_baseline: int
):
    # Contributions
    sleep_gain = SLEEP_HOURS_W * (sleep_hours - 7.0) + SLEEP_QUALITY_W * sleep_quality
    activity_load = STEPS_W * steps + MODERATE_W * moderate_min + VIGOROUS_W * vigorous_min
    hr_stress = max(0.0, (rhr - rhr_baseline)) * HR_STRESS_W

    raw = 50.0 + sleep_gain - activity_load - hr_stress
    score = max(0.0, min(100.0, round(raw, 1)))
    return score, sleep_gain, activity_load, hr_stress, round(raw, 1)

st.set_page_config(page_title="Body Battery (Demo)", page_icon="🔋", layout="centered")
st.title("🔋 Body Battery (Demo)")
st.caption("Toy model for educational purposes — not medical advice.")

with st.sidebar:
    st.header("Settings")
    st.write("Tweak the coefficients at the top if the scale feels off.")

st.subheader("Sleep (last night)")
col1, col2 = st.columns(2)
with col1:
    sleep_hours = st.slider("Hours of sleep", 0.0, 12.0, 7.0, 0.25)
with col2:
    sleep_quality = st.slider("Sleep quality (0–100)", 0, 100, 70, 1)

st.subheader("Activity (yesterday)")
c1, c2, c3 = st.columns(3)
with c1:
    steps = st.number_input("Steps", min_value=0, value=8000, step=500)
with c2:
    moderate_min = st.number_input("Moderate minutes", min_value=0, value=30, step=5)
with c3:
    vigorous_min = st.number_input("Vigorous minutes", min_value=0, value=10, step=5)

st.subheader("Heart Rate (today)")
c4, c5 = st.columns(2)
with c4:
    rhr = st.number_input("Resting HR (bpm)", min_value=30, max_value=120, value=60, step=1)
with c5:
    rhr_baseline = st.number_input("Baseline resting HR (bpm)", min_value=30, max_value=120, value=58, step=1)

score, sleep_gain, activity_load, hr_stress, raw = compute_body_battery(
    sleep_hours, sleep_quality, steps, moderate_min, vigorous_min, rhr, rhr_baseline
)

st.markdown("---")
st.metric(label="Estimated Body Battery", value=f"{score} / 100")
st.progress(int(score))

st.markdown("### What influenced this?")
with st.expander("Show contributions"):
    st.write(
        f"- **Sleep gain**: +{sleep_gain:.1f}\n"
        f"- **Activity load**: −{activity_load:.1f}\n"
        f"- **HR stress**: −{hr_stress:.1f}\n"
        f"- **Base**: +50.0\n"
        f"- **Unclamped total**: {raw:.1f}\n"
        f"- **Final (clamped 0–100)**: {score:.1f}"
    )
