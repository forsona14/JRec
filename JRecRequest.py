class JRecRequest:
    def __init__(self, article):
        self.article = article
        self.doc_id = article.doc_id
        self.text = article.text