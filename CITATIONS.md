# Citations & Attributions

This project acknowledges and cites the following foundational datasets, open-source libraries, models, and references:

---

## 1. Primary Dataset
- **Dataset**: *Customer Support on Twitter*
- **Authors**: ThoughtVector (Kaggle Dataset)
- **Kaggle URL**: [https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)
- **Hugging Face Mirror**: `SunidhiSriram/twcs` ([https://huggingface.co/datasets/SunidhiSriram/twcs](https://huggingface.co/datasets/SunidhiSriram/twcs))
- **Usage**: Source of historical customer queries and official `@AppleSupport` agent replies (October–November 2017).

---

## 2. Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Authors**: Nils Reimers and Iryna Gurevych (UKP Lab, TU Darmstadt)
- **Citation**:
  ```bibtex
  @inproceedings{reimers-2019-sentence-bert,
      title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
      author = "Reimers, Nils and Gurevych, Iryna",
      booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
      month = "11",
      year = "2019",
      publisher = "Association for Computational Linguistics",
      url = "https://arxiv.org/abs/1908.10084",
  }
  ```
- **Usage**: Dense vector representation for intent classification, KMeans clustering, and semantic retrieval over historical resolutions.

---

## 3. Core Software Libraries
- **Scikit-Learn**:
  - Pedregosa et al., *Scikit-learn: Machine Learning in Python*, JMLR 12, pp. 2825-2830, 2011.
  - Used for `LogisticRegression`, `CalibratedClassifierCV`, `TfidfVectorizer`, `KMeans`, and evaluation metrics (`classification_report`, `f1_score`).
- **Pandas & NumPy**:
  - Wes McKinney, *Data Structures for Statistical Computing in Python*, Proceedings of the 9th Python in Science Conference, 2010.
  - Used for thread reconstruction, columnar filtering, and matrix operations.
- **PyArrow**:
  - Apache Arrow foundation for high-performance parquet read/write.
- **Tabulate & TQDM**:
  - Terminal formatting and progress tracking.

---

## 4. Official Brand Knowledge Base Anchors
- All diagnostic troubleshooting URLs embedded in the Reply Generator are official Apple Support canonical resources:
  - Software Update: `https://support.apple.com/ios/update`
  - Battery & Power: `https://support.apple.com/iphone/repair/battery-replacement`
  - Apple ID & iCloud: `https://iforgot.apple.com`
  - Hardware & Genius Bar: `https://getsupport.apple.com`
  - Network & Wi-Fi: `https://support.apple.com/HT204051`
  - Billing & App Store: `https://reportaproblem.apple.com`
  - Storage Management: `https://support.apple.com/HT201656`
