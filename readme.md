# SubReconciler

**SubReconciler** is a Python tool for subtitle reconciliation that aligns a text file (translation, script, OCR, etc.) with an existing timing file, **without ever breaking order or overwriting already validated matches**.

Unlike conventional tools, SubReconciler uses **immutable anchors**, ensuring stable, deterministic, and explainable synchronization.

---

## ✨ Key Features

- 🔒 **Immutable Anchors**  
  Reliable matches (rank-fusion) are never modified.

- 🔁 **Bidirectional Reconciliation**
  - text → timing
  - timing → text  
  with rank fusion for maximum reliability.

- 🧩 **Intelligent Gap Filling**  
  Fills only logical gaps between two compatible anchors.

- 📐 **Controlled Linear Spread**  
  Remaining lines are distributed **evenly in time**, only between two anchors.

- 🚫 **No out-of-order lines**
  - No temporal overlaps
  - No replacement of already matched lines
  - Strict monotonicity between text and timing

- 📝 **Embedded annotations**
  Each subtitle indicates its origin:
  - `rank`
  - `gap`
  - `spread`

- ⚙️ **Simple configuration via `config.ini`**

---

## ▶️ Usage

```bash
python main.py
```

The reconciled file will be generated in:
```
files/output/final.srt
```

---

## 🧠 Algorithm Philosophy

1. **Rank Fusion**
   - Create reliable anchors text ↔ timing
2. **Gap Filling**
   - Fill only if text and timing progress together
3. **Linear Spread**
   - Evenly distribute remaining lines between two anchors
4. **Final Build**
   - No overwriting
   - No disorder
   - Fully explainable result

> SubReconciler prioritizes **semantic safety** over maximum coverage.

---

## 📌 Ideal Use Cases

- Fansub / anime resynchronization
- OCR + existing subtitles
- Script / dialogue alignment
- Partially damaged subtitle restoration
- Projects needing deterministic results

---

## 🛠️ Dependencies

- Python 3.9+
- `pysrt`
- `tqdm`
- `colorama`

Install with:
```bash
pip install pysrt tqdm colorama
```

---

## 📜 License

Personal / experimental project.  
Free to use and modify.

---

## ✍️ Author

Designed with obsession for:
- order
- stability
- and refusal of destructive “best guess”

**SubReconciler** does not guess.  
It **reconciles**.

