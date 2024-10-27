from langchain_community.document_loaders import PyPDFLoader

def load_document_langchain(filename:str)->None:
    loader = PyPDFLoader("./uploads/"+filename)
    pages = loader.load_and_split()
    print(len(pages))

