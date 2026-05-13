import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import math
import os

# --- 1 & 2: DATA LAYER ---
def generate_curriculum():
    # 8 semesters, 5 courses per semester, 30 ECTS per semester
    curriculum = {}
    for sem in range(1, 9):
        courses = []
        for c in range(1, 6):
            courses.append({
                "name": f"Ders {sem}0{c}",
                "ects": 6,
                "difficulty": np.random.uniform(0.8, 1.2)
            })
        curriculum[sem] = courses
    return curriculum

def calculate_grade(score):
    if score >= 90: return "AA", 4.0
    elif score >= 85: return "BA", 3.5
    elif score >= 80: return "BB", 3.0
    elif score >= 75: return "CB", 2.5
    elif score >= 70: return "CC", 2.0
    elif score >= 60: return "DC", 1.5
    elif score >= 50: return "DD", 1.0
    elif score >= 40: return "FD", 0.5
    else: return "FF", 0.0

# --- 3: ACTORS ---
class Student:
    def __init__(self, energy=100, iq=1.0, motivation=100):
        self.energy = energy
        self.iq = iq
        self.motivation = motivation
        self.burnout = 0
        self.cumulative_fatigue = 0
        self.gpa = 0.0

class Course:
    def __init__(self, data):
        self.name = data["name"]
        self.ects = data["ects"]
        self.difficulty = data["difficulty"]
        self.knowledge = 0.0 # 0 to 100
        self.midterm = 0.0
        self.final = 0.0

class SimulationCore:
    def __init__(self, sleep_hours, social_hours, cram_days, part_time_hours=0, caffeine_cups=0):
        self.sleep_hours = sleep_hours
        self.social_hours = social_hours
        self.cram_days = cram_days
        self.part_time_hours = part_time_hours
        self.caffeine_cups = caffeine_cups
        self.student = Student()
        self.curriculum = generate_curriculum()
        self.history = []
        self.exam_results = []
    
    def run(self):
        for semester in range(1, 9):
            active_courses = [Course(c) for c in self.curriculum[semester]]
            
            for day_in_sem in range(1, 99): # 14 weeks = 98 days
                global_day = (semester - 1) * 98 + day_in_sem
                
                # Caffeine & Part-Time Job Logic
                caffeine_boost = min(0.3, self.caffeine_cups * 0.05)
                caffeine_crash = self.caffeine_cups * 0.8
                
                # Energy & Fatigue logic (Yerkes-Dodson & Sleep Deprivation)
                sleep_deficit = max(0, 7 - self.sleep_hours) + (caffeine_crash / 2)
                self.student.cumulative_fatigue += sleep_deficit * 2.5
                
                # Part time job consumes energy and time
                job_exhaustion = (self.part_time_hours / 7) * 1.5
                self.student.cumulative_fatigue += job_exhaustion
                self.student.cumulative_fatigue = min(100, self.student.cumulative_fatigue)
                
                # Efficiency based on fatigue + caffeine boost
                efficiency = math.exp(-0.05 * self.student.cumulative_fatigue) + caffeine_boost
                efficiency = min(1.0, max(0.0, efficiency)) # Cap between 0 and 1
                
                # Motivation logic based on social hours & financial stress
                base_motivation_change = 0
                if self.social_hours < 5:
                    base_motivation_change -= 1.5
                elif 5 <= self.social_hours <= 15:
                    base_motivation_change += 1.0
                else:
                    base_motivation_change -= 0.5 # Too much socializing
                
                # Penalize motivation if overworked
                if self.part_time_hours > 20:
                    base_motivation_change -= 1.0
                elif self.part_time_hours > 0 and self.part_time_hours <= 15:
                    base_motivation_change += 0.2 # Small financial comfort boost
                
                self.student.motivation += base_motivation_change
                self.student.motivation = max(0, min(100, self.student.motivation))
                self.student.burnout = 100 - self.student.motivation
                
                # Attendance Risk (Skipping classes due to extreme fatigue)
                attendance_penalty = 1.0
                if self.student.cumulative_fatigue > 85:
                    attendance_penalty = 0.5 # Devamsızlık riski (skipping)
                elif self.student.cumulative_fatigue > 95:
                    attendance_penalty = 0.2
                
                # Study strategy
                is_cramming = False
                if (49 - self.cram_days <= day_in_sem < 49) or (98 - self.cram_days <= day_in_sem < 98):
                    is_cramming = True
                
                base_study = 2
                if is_cramming:
                    base_study = 6
                
                daily_job_hours = self.part_time_hours / 7
                available_time_ratio = max(0, (24 - self.sleep_hours - daily_job_hours - 4) / 10)
                
                actual_study_hours = base_study * (self.student.motivation / 100) * available_time_ratio * attendance_penalty
                
                for course in active_courses:
                    # Learning progression
                    daily_learning = (actual_study_hours / len(active_courses)) * efficiency * self.student.iq / course.difficulty
                    course.knowledge += daily_learning * 3.5
                    course.knowledge = min(100, course.knowledge)
                    
                    # Midterm Exam (Day 49)
                    if day_in_sem == 49:
                        score = course.knowledge * 0.8 + np.random.normal(0, 10) - (self.student.cumulative_fatigue * 0.2)
                        score = max(0, min(100, score))
                        course.midterm = score
                    
                    # Final Exam (Day 98)
                    if day_in_sem == 98:
                        score = course.knowledge * 0.8 + np.random.normal(0, 10) - (self.student.cumulative_fatigue * 0.2)
                        score = max(0, min(100, score))
                        course.final = score
                        
                        final_grade = course.midterm * 0.4 + course.final * 0.6
                        letter, points = calculate_grade(final_grade)
                        
                        self.exam_results.append({
                            "semester": semester,
                            "course": course.name,
                            "midterm": course.midterm,
                            "final": course.final,
                            "grade": final_grade,
                            "letter": letter,
                            "points": points,
                            "sleep_dep": self.student.cumulative_fatigue
                        })
                
                # Recovery
                if self.sleep_hours > 7:
                    self.student.cumulative_fatigue -= (self.sleep_hours - 7) * 2
                    self.student.cumulative_fatigue = max(0, self.student.cumulative_fatigue)
                
                self.history.append({
                    "Gün": global_day,
                    "Dönem": semester,
                    "Uyku_Saati": self.sleep_hours,
                    "Çalışma_Saati": actual_study_hours,
                    "Anlık_Motivasyon": self.student.motivation,
                    "Kümülatif_Yorgunluk": self.student.cumulative_fatigue,
                    "Tükenmişlik": self.student.burnout
                })
                
        df = pd.DataFrame(self.history)
        df.to_csv("academic_sim_data.csv", index=False)
        
        exam_df = pd.DataFrame(self.exam_results)
        if not exam_df.empty:
            self.student.gpa = (exam_df["points"] * 6).sum() / (len(exam_df) * 6)
            passed = len(exam_df[exam_df["points"] >= 1.0])
            grad_prob = (passed / len(exam_df)) * 100
        else:
            self.student.gpa = 0
            grad_prob = 0
            
        return df, exam_df, self.student.gpa, grad_prob

# --- 4 & 6: STREAMLIT UI ---
st.set_page_config(page_title="Öğrenci Akademik Simülasyonu", page_icon="🎓", layout="wide")

st.title("🎓 Sistem Dinamiği: 4 Yıllık Akademik Hayat Simülasyonu")
st.markdown("""
Bu simülasyon, bir üniversite öğrencisinin 4 yıllık (8 dönem) eğitim hayatını modellemektedir. 
Amaç; zaman, enerji ve çalışma stratejisi gibi faktörlerin, dönem sonu başarı durumu (GPA), 
tükenmişlik sendromu (Burnout) ve mezuniyet olasılığı üzerindeki etkisini analiz etmektir.
*(Yerkes-Dodson Yasası ve Uyku Yoksunluğu araştırmaları temel alınmıştır).*
""")

st.sidebar.header("🎛️ Temel Kontrol Paneli")
sleep_hours = st.sidebar.slider("Günlük Uyku Süresi (Saat)", 4.0, 10.0, 7.0, 0.5)
social_hours = st.sidebar.slider("Haftalık Sosyal Zaman (Saat)", 0, 40, 10, 1)
cram_days = st.sidebar.slider("Sınava Kaç Gün Kala Yoğun Çalışılacak?", 1, 14, 3, 1)

st.sidebar.header("⚙️ Gelişmiş Faktörler")
with st.sidebar.expander("Ekstra Etkenleri Ayarla", expanded=False):
    part_time_hours = st.slider("Haftalık Yarı Zamanlı İş (Saat)", 0, 30, 0, 5, help="Maddi rahatlık sağlar ama zaman ve enerjiden çalar.")
    caffeine_cups = st.slider("Günlük Kafein/Kahve (Fincan)", 0, 10, 1, 1, help="Anlık verimliliği artırır ancak uyku kalitesini düşürerek uzun vadeli yorgunluk (crash) yaratır.")

# Check session state
if "simulation_run" not in st.session_state:
    st.session_state["simulation_run"] = False

# Download button for previous run if exists
if st.session_state["simulation_run"]:
    st.sidebar.divider()
    if os.path.exists("academic_sim_data.csv"):
        with open("academic_sim_data.csv", "rb") as file:
            st.sidebar.download_button(
                label="💾 Sonuçları CSV Olarak İndir",
                data=file,
                file_name="academic_sim_data.csv",
                mime="text/csv"
            )

# Run simulation button
if st.sidebar.button("🚀 Simülasyonu Başlat", type="primary"):
    with st.spinner("4 Yıllık Eğitim Hayatı Simüle Ediliyor..."):
        sim = SimulationCore(sleep_hours, social_hours, cram_days, part_time_hours, caffeine_cups)
        df, exam_df, final_gpa, grad_prob = sim.run()
        
        st.session_state["df"] = df
        st.session_state["exam_df"] = exam_df
        st.session_state["final_gpa"] = final_gpa
        st.session_state["grad_prob"] = grad_prob
        st.session_state["simulation_run"] = True

if not st.session_state["simulation_run"]:
    st.info("👈 Lütfen sol panelden parametreleri ayarlayın ve 'Simülasyonu Başlat' butonuna tıklayarak analizi başlatın.")
    st.stop()

df = st.session_state["df"]
exam_df = st.session_state["exam_df"]
final_gpa = st.session_state["final_gpa"]
grad_prob = st.session_state["grad_prob"]

# --- TOP METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("Tahmini Mezuniyet GPA", f"{final_gpa:.2f} / 4.00")
col2.metric("Mezuniyet Olasılığı", f"%{grad_prob:.0f}")
col3.metric("Ortalama Tükenmişlik", f"%{df['Tükenmişlik'].mean():.0f}")

st.markdown("### Mezuniyet İlerlemesi")
# Progress bar turns red if probability is low
if grad_prob < 50:
    st.markdown(f"""
        <style>
        .stProgress > div > div > div > div {{
            background-color: #ff4b4b;
        }}
        </style>
    """, unsafe_allow_html=True)
elif grad_prob < 80:
    st.markdown(f"""
        <style>
        .stProgress > div > div > div > div {{
            background-color: #ffa500;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <style>
        .stProgress > div > div > div > div {{
            background-color: #00cc66;
        }}
        </style>
    """, unsafe_allow_html=True)

st.progress(int(grad_prob) / 100)

st.divider()

# --- CHARTS ---
st.subheader("📊 Analiz Grafikleri")
tab1, tab2, tab3 = st.tabs(["📉 GPA ve Tükenmişlik", "🛏️ Uyku ve Başarı", "🔥 Verimlilik Haritası"])

with tab1:
    st.markdown("#### 4 Yıl Boyunca Tükenmişlik ve GPA Gelişimi")
    sem_df = df.groupby("Dönem")["Tükenmişlik"].mean().reset_index()
    exam_sem_df = exam_df.groupby("semester")["points"].mean().reset_index()
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=sem_df["Dönem"], y=sem_df["Tükenmişlik"], mode='lines+markers', name="Tükenmişlik Seviyesi (%)", line=dict(color='red')))
    # Scale GPA to 0-100 for comparison
    fig1.add_trace(go.Scatter(x=exam_sem_df["semester"], y=exam_sem_df["points"] * 25, mode='lines+markers', name="GPA (100 Üzerinden)", line=dict(color='blue')))
    fig1.update_layout(xaxis_title="Dönem", yaxis_title="Seviye (0-100)", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.markdown("#### Uyku Eksikliği ve Sınav Notları Korelasyonu")
    fig2 = px.scatter(
        exam_df, x="sleep_dep", y="grade", color="letter", 
        trendline="ols",
        labels={"sleep_dep": "Sınav Günü Kümülatif Yorgunluk", "grade": "Sınav Notu", "letter": "Harf Notu"}
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("#### Uyku Süresi ve Haftanın Günlerine Göre Verimlilik")
    # Simulate a heatmap data
    sleep_range = np.arange(4, 11)
    days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    heat_data = np.zeros((len(sleep_range), len(days)))
    
    for i, s in enumerate(sleep_range):
        for j, d in enumerate(days):
            weekend_bonus = 0.15 if j >= 5 else 0
            dep = max(0, 7 - s)
            eff = math.exp(-0.05 * dep * 10) + weekend_bonus
            heat_data[i, j] = min(1.0, max(0.0, eff))
            
    fig3, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(heat_data, xticklabels=days, yticklabels=sleep_range, cmap="RdYlGn", annot=True, fmt=".2f", ax=ax)
    ax.set_xlabel("Haftanın Günleri")
    ax.set_ylabel("Uyku Süresi (Saat)")
    st.pyplot(fig3)

st.success("Tüm veriler başarıyla analiz edildi ve 'academic_sim_data.csv' olarak kaydedildi. Sol menüden indirebilirsiniz.")
