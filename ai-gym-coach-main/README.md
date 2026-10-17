# 🏋️‍♂️ AI Real-Time GYM Coach & Pose Trainer

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=MrAditya-Singh/AiCoach&branch=main&mainModule=app.py)
[![GitHub stars](https://img.shields.io/github/stars/MrAditya-Singh/AiCoach?style=social)](https://github.com/MrAditya-Singh/AiCoach)

An intelligent, real-time AI fitness coach powered by **Computer Vision (MediaPipe)** and **Generative AI (Groq LLM + Text-to-Speech)**. The app tracks exercise repetitions, evaluates posture and form angles in real time via your webcam/phone, and delivers proactive voice coaching feedback to help you maintain optimal form and prevent injury.

---

## 🚀 Live Application & Deployment

### 1. Run / Deploy with 1-Click (Streamlit Community Cloud)
Click the badge below to immediately deploy and launch this app on Streamlit Cloud for free:

[![Deploy with Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=MrAditya-Singh/AiCoach&branch=main&mainModule=app.py)

**Deployment Settings on Streamlit Cloud:**
- **Repository:** `MrAditya-Singh/AiCoach`
- **Branch:** `main`
- **Main file path:** `app.py`
- **Advanced Settings -> Secrets:**
  ```toml
  GROQ_API_KEY = "your_groq_api_key_here"
  ```

---

## ✨ Features

- 📹 **Real-Time Video Stream (WebRTC):** Ultra-low latency webcam stream processed using `streamlit-webrtc`.
- 🤖 **MediaPipe 3D Pose Landmarker:** 33 landmark points tracked with sub-second accuracy to compute joint angles.
- 🏋️ **Supported Exercises:**
  - **Squats:** Knee flexion, back angle tracking, and depth validation.
  - **Push-ups:** Elbow angle, body alignment, and hip posture checks.
  - **Biceps Curls (Dumbbell):** Full range of motion, shoulder stability, and body swing detection.
  - **Shoulder Press:** Overhead extension tracking and back arch monitoring.
  - **Lunges:** Front knee angle, torso uprightness, and balance evaluation.
- 🗣️ **AI Voice Coaching:** Real-time motivational and corrective voice feedback using **Groq Fast LLM** and **gTTS audio generation**.
- 📊 **Workout Analytics & History:** Auto-logging of reps, sets, and workout duration per user using local SQLite storage.
- 🎨 **Modern Dark UI:** High-performance, polished UI with custom typography.

---

## 📂 Project Structure

```
├── app.py                     # Root entrypoint for 1-click Streamlit Cloud deployment
├── requirements.txt           # Python dependencies (Streamlit, MediaPipe, OpenCV, Groq, gTTS)
├── packages.txt               # OS-level libraries (libgl1, libglib2.0-0, libsm6, libxext6)
├── .gitignore                 # Standard Python, environment & cache ignore patterns
├── README.md                  # Project documentation & deployment guide
├── LandingPage/               # Showcase landing page (HTML5 / CSS3 / Animations)
│   ├── index.html
│   ├── style.css
│   └── fonts/
└── Main App/                  # Core Streamlit application
    ├── main.py                # Main Streamlit app logic
    ├── core/                  # Base exercise interface classes
    ├── detectors/             # Exercise-specific angle & rep detector logic
    │   ├── squat.py
    │   ├── pushup.py
    │   ├── biceps_curl.py
    │   ├── shoulder_press.py
    │   └── lunges.py
    ├── ml_models/             # MediaPipe Pose Landmarker full model task file
    ├── services/              # Auth, state, persistence, UI, and voice coaching pipelines
    └── static/                # CSS stylesheet & custom fonts
```

---

## 🛠️ Local Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/MrAditya-Singh/AiCoach.git
cd AiCoach
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (or set `GROQ_API_KEY`):
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```
*(Get your free API key at [Groq Console](https://console.groq.com/keys))*

### 5. Run the application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying the Landing Page to GitHub Pages

To host the visual showcase landing page:
1. Go to your GitHub repository: [https://github.com/MrAditya-Singh/AiCoach](https://github.com/MrAditya-Singh/AiCoach)
2. Click **Settings** > **Pages**.
3. Under **Build and deployment** > **Source**, choose **Deploy from a branch**.
4. Set branch to `main` and directory to `/ (root)`.
5. The landing page will be live at: `https://mraditya-singh.github.io/AiCoach/LandingPage/`

---

## 👨‍💻 Author

- **Aditya Singh**
- GitHub: [@MrAditya-Singh](https://github.com/MrAditya-Singh)
- Email: [mradityasinghofficial1@gmail.com](mailto:mradityasinghofficial1@gmail.com)

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).