from requests_html import HTML

def get_shows_html(doc):
    html = HTML(html=doc)

    # deduplicate movie names as they could be repeated across the text
    content = set()

    for elem in html.find('font[style*="italic"]'):
        title = elem.text.strip()
        if title and title != ".":
            if ',' in title:
                names = title.split(',')
                for name in names:
                    name = name.strip()
                    if name:
                        content.add(name)
            else:
                content.add(title.strip())

    return content

def get_shows_nlp(doc):
    import spacy

    nlp = spacy.load("en_core_web_lg")
    doc = nlp(doc)

    content = set()
    for ent in doc.ents:
        # Uncomment to see additional information about each detected
        # entity
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        content.add(ent.text)

    return content

def extract_content_section(filepath):
    content_html = []
    content_txt = []
    with open(filepath, 'r') as fp:
        doc = fp.read()
        html = HTML(html=doc)
        is_content_div = False
        for elem in html.find('div'):
            if elem.text == 'Content':
                is_content_div = True
                continue

            if is_content_div:
                style = elem.attrs.get('style', '')
                if 'font-size:18pt' in style:
                    is_content_div = False
                    break

                if 'line-height:120%' and 'font-size:11pt' in style\
                   and 'padding-bottom:6px' not in style:
                    content_html.append(elem.html)
                    content_txt.append(elem.text.strip())

    return ("\n".join(content_html),
            "\n".join(content_txt).replace("\n"," "))

def get_movie_sentences(movies, text):
    sentences = text.split(". ")
    movie_sentences = {}
    for movie in sorted(list(movies)):
        if not movie in movie_sentences:
            movie_sentences[movie] = []

        for sentence in sentences:
            if movie in sentence:
                movie_sentences[movie].append(sentence)

    return movie_sentences

def emit_html(movie_sentences):
    for movie in sorted(movie_sentences.keys()):
        print(f"<li title='{'. '.join(movie_sentences[movie]).strip()}'>{movie}</li>")

if __name__ == '__main__':
    (html, text) = extract_content_section('data/8K-Exhibit-91-2019-Q1.html')
    print("Results using html parsing:")
    movies_html = get_shows_html(html)
    print(movies_html)
    print("")
    print("Results using nlp named entity detection:")
    movies_nlp = get_shows_nlp(text)
    print(movies_nlp)
