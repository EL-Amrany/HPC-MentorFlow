# HPC-Tutor 🧠🚀

**Enhancing Institutional HPC Competencies through an AI Tutoring System**

HPC-Tutor is an AI-powered, adaptive learning platform designed to elevate skills in High Performance Computing (HPC). It supports role-based progression, Bloom-aligned learning objectives, and interactive tutoring using LLMs and Retrieval-Augmented Generation (RAG).

---

## 📚 Features

- 🎓 **Role-Specific Competency Paths**  
  Tailored learning modules for *HPC AI Specialists* and *Computational Chemistry Specialists*.

- 📈 **Adaptive Progression Engine**  
  Learners advance through levels (Apprentice → Practitioner → Competent) based on skill mastery and quiz performance.

- 🤖 **LLM-Based Interactive Tutoring**  
  Integrated chatbot delivers lesson content, adaptive quizzes, and real-time feedback, aligned with Bloom's Taxonomy.

- 📁 **Document-Grounded RAG Integration**  
  Answers are grounded in curated institutional documents using vector search and LangChain.

- 🧪 **Multi-Skill Module Tracking**  
  Supports learning objective tracking by both module *and* skill level (e.g., A1@Remember, A1@Apply).

- 🔒 **Ethical AI & Data Privacy**  
  Built with ethical principles including fairness, transparency, and hallucination mitigation.

---

## 🧰 Tech Stack

| Layer         | Stack                                  |
|--------------|-----------------------------------------|
| Backend      | Flask, SQLAlchemy, Flask-Login          |
| Frontend     | Jinja2, Tailwind CSS, HTML/JS           |
| AI Backend   | OpenAI GPT-4 / GPT-4o, LangChain         |
| Vector Store | FAISS or Chroma (plug-and-play)         |
| Database     | SQLite (can scale to PostgreSQL)        |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/hpc-tutor.git
cd hpc-tutor
