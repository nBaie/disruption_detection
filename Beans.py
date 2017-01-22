class doc_bean:
    DocumentId = 0
    Vector = []
    Text = ""
    Decision = 0.0
    URL = ""
    def __init__(self,DocumentId,Vector,Text,Decision,url):
        self.DocumentId=DocumentId
        self.Vector=Vector
        self.Text=Text
        self.Decision=Decision
        self.URL = url

class doc_interessant:
    DocumentId = 0
    Text = ""
    def __init__(self,DocumentId,Text):
        self.DocumentId=DocumentId
        self.Text=Text