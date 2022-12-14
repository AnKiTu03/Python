
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from heapq import nlargest
from flask import Flask, render_template, request

app = Flask("Text_summarizer")






@app.route("/")
def home():
    return render_template("home.html")


@app.route("/process", methods=["POST"])
def prediction():
    text = request.form["z1"]
    stopwords = list(STOP_WORDS)

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.text for token in doc]

    word_frequencies = {}

    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = [sent for sent in doc.sents]

    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    from heapq import nlargest
    select_length = int(len(sentence_tokens) * 0.3)

    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-one-to-many-mmt")
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-one-to-many-mmt", src_lang="en_XX")


    model_inputs = tokenizer(summary, return_tensors="pt")

    # translate from English to Hindi
    generated_tokens = model.generate(
        **model_inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id["hi_IN"]
    )

    translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    print(translation)

    # return summary
    return render_template('output.html', summary=translation)

    # print(summarise(text))


app.run(host="localhost", port=3000)
