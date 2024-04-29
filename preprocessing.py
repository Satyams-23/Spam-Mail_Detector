import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk

nltk.download('punkt')
nltk.download('stopwords')

ps = PorterStemmer()

def transform_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    processed_tokens = []
    for token in tokens:
        if token.isalnum() and token not in stopwords.words('english') and token not in string.punctuation:
            processed_tokens.append(ps.stem(token))
    return " ".join(processed_tokens)
