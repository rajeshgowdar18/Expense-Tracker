# model.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import pickle
from train_data import training_data

def train_model():
    texts  = [t[0] for t in training_data]
    labels = [t[1] for t in training_data]

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("clf",   MultinomialNB())
    ])

    model.fit(texts, labels)

    # Save to disk
    with open("expense_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model trained and saved!")
    return model

def load_model():
    try:
        with open("expense_model.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return train_model()

def predict_category(model, description):
    return model.predict([description.lower()])[0]