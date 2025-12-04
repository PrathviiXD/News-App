# BiasRadar  
A simple web app that shows how different news outlets talk about the **same topic**.  
It analyzes real news articles, checks the sentiment, emotion, and subjectivity, and displays the results on an interactive radar chart.

This project is built to help people quickly understand **media bias** and how different sources frame the same event.

---

## 🚀 Live Demo  
Frontend (Netlify): https://biasradar.netlify.app/  
Backend API (Render): https://news-app-6-5d84.onrender.com

---

## 🧠 What This App Does  
You type a topic (example: *"AI regulation"*, *"Climate change"*, *"India budget"*).  
The app:

1. Fetches real news articles using **NewsAPI**
2. Groups them by **news source** (BBC, CNN, TOI, Reuters, etc.)
3. Runs simple NLP to calculate:
   - **Sentiment** (how positive or negative it sounds)
   - **Subjectivity** (opinion vs facts)
   - **Emotion** (fear, anger, joy, or neutral)
   - **Emotion intensity** (how emotional the language is)
4. Shows everything in:
   - A **radar chart**
   - A **detailed table**

This helps compare how each outlet presents the same story.

---

## 🎯 Why I Built This  
Most news apps only show the articles.  
They don’t tell you **how** the news is written.

BiasRadar gives a quick visual way to see:

- Which outlets are emotional  
- Which outlets are neutral  
- Who is more opinionated  
- Who is more positive or negative  
- How political leaning affects coverage  

It’s useful for learning, research, personal awareness, and especially for showing technical skills.

---

## 🛠️ Tech Stack  
### **Frontend**
- HTML  
- CSS  
- JavaScript  
- Chart.js (for radar visualizations)  
- Hosted on **Netlify**

### **Backend**
- FastAPI  
- Python  
- Requests (for NewsAPI calls)  
- VADER (sentiment analysis)  
- Hosted on **Render**

### **External API**
- **NewsAPI** (https://newsapi.org/)

---


---

## 🔍 How To Use

1. Open the live frontend link  
2. Enter any topic (example: "AI", "Climate change", "Stock market")  
3. Click **Analyze bias**  
4. View:
   - Radar chart → visual comparison  
   - Table → detailed data  
5. Try different topics to see how media coverage changes

---

## 🧪 Example Topics to Try
- **AI regulation**  
- **India elections**  
- **Budget 2025**  
- **Bitcoin crash**  
- **Israel Gaza**  
- **Climate change**  

Each topic will show different emotional and tonal patterns from different outlets.

---

## 🧩 Features

- Real-time article fetching  
- Per-source sentiment scoring  
- Emotion detection (fear, anger, joy, neutral)  
- Subjectivity measurement  
- Visual radar comparison  
- Source political-lean tags  
- Fully deployed full-stack setup  

---

## 📘 How the Analysis Works (Simple Explanation)

**Sentiment:**  
Uses VADER to check if the article is positive, negative, or neutral.

**Subjectivity:**  
Counts opinion-style words (“think”, “believe”, “should”, etc.).

**Emotion:**  
Looks for emotion-related words:
- fear → “risk”, “panic”, “worried”
- anger → “corruption”, “blame”, “attack”
- joy → “success”, “growth”, “win”

**Emotion Intensity:**  
How many emotional words vs neutral words.

The app doesn’t claim to be perfect — it gives a **quick overview**, not a deep academic analysis.

---

## 🧩 API Endpoint (Backend)

### **POST** `/api/analyze`
Send:
```json
{
  "topic": "AI regulation",
  "language": "en",
  "page_size": 40
}

