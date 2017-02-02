class JRecRequest:
    def __init__(self, article):
        self.article = article
        # ID used for articles, paragraphs or sentences
        # Example: 'k10010731741000_para3'
        self.doc_id = article.doc_id
        # ID used for url
        # Example: 'k10010731741000'
        self.id = self.doc_id[:15]
        self.text = article.text