# 🧠 AI Data Visualization Tool

Projekts nodrošina datu augšupielādi, analīzi un vizualizāciju, izmantojot mākslīgā intelekta metodes.

<p align="center">
  <img src="https://img.shields.io/badge/ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  <img src="https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E" />
  <img src="https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white" />
</p>

---
## 🔍 Projekta pārskats

### Ko dara:
Lietotājs var augšupielādēt strukturētus datu failus (CSV vai Excel), sistēma automātiski apstrādā datus, izvēlas piemērotākos grafikus un attēlo tos interaktīvā formā.
### Kā strādā:
Backend izmanto Python un Flask, datu analīzei – Pandas, mākslīgā intelekta funkcionalitātei – lokāls LLM modelis ar Ollama, frontendā tiek izmantots Chart.js vizualizācijai.
### Ko saņem lietotājs:
Interaktīvu datu vizualizāciju, automātiski ģenerētus grafikus un ātru datu analīzi bez nepieciešamības manuāli izvēlēties vizualizācijas veidu.

---
## 🖥 Kā lietot

<img width="2560" height="1259" alt="instruction" src="https://github.com/user-attachments/assets/2be038bd-6ae7-46a8-9451-e504c2af7f9e" />


---
## 🧩 Sistēmas arhitektūra

```mermaid
flowchart LR
    A["Lietotājs (Browser)"]
    B["Frontend (HTML/CSS/JS + Chart.js)"]
    C["Backend (Flask API)"]
    D["Datu apstrāde (Pandas)"]
    E["AI modulis (Ollama LLM)"]

    A --> B
    B -->|HTTP pieprasījumi| C
    C --> D
    C --> E
    D --> C
    E --> C
    C -->|JSON atbilde| B
    B -->|Grafiki| A
```

*Attēls: Projekta augsta līmeņa arhitektūra – lietotāja pieprasījumi, datu apstrāde un AI lēmumu pieņemšana.

---
## ⚙️ Tehnoloģiju steks

| Komponents             | Tehnoloģija             |
| ---------------------- | ----------------------- |
| **Backend**            | Python 3.10+, Flask     |
| **Datu apstrāde**      | Pandas, NumPy           |
| **AI modulis**         | Ollama, LLM             |
| **Frontend**           | HTML5, CSS3, JavaScript |
| **Datu vizualizācija** | Chart.js                |

---
## 🚀 Uzstādīšana

### 1. Klonē repozitoriju:
```bash
git clone https://github.com/SairnaD/AI-based-data-visualization.git
cd <project-folder>
```

### 2. Palaid uzstādīšanas skriptu:
```bash
bash setup.sh
```

### Uzstādīšana automātiski:
- izveido virtuālo vidi (venv)
- uzinstalē Python bibliotēkas
- uzinstalē Ollama (ja nepieciešams)
- lejupielādē AI modeli

---
## ▶️ Sistēmas palaišana

### 1. Aktivizē virtuālo vidi:
```bash
source venv/bin/activate
```

### 2. Palaid serveri:
```bash
python app.py
```
### 3. Atver pārlūkā:
```bash
http://localhost:5000
```

---
## 📝 API apraksts

- **POST /upload** – pieņem datu failu un atgriež ieteikumus par vizualizāciju
- **GET /data** – atgriež apstrādātus datus grafiku attēlošanai

---
## 🧠 Mākslīgā intelekta izmantošana

Sistēma izmanto lokālu lielo valodas modeli (LLM) ar Ollama, lai:
- analizētu datu kolonnu tipus
- interpretētu datu tipus
- izvēlētos optimālos vizualizācijas veidus

---
## ⚠️ Ierobežojumi

- Atbalsta tikai CSV un XLSX failus
- Lieliem datu apjomiem iespējama ilgāka apstrāde
- Nepieciešama lokāla Ollama darbība
