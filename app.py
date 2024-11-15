import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pdfplumber
import tempfile
from pathlib import Path
import json
from urllib.parse import urlparse
import spacy
from docx import Document
import time

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_from_url(self, url):
        """Extract text content from procurement websites"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Extract text and clean it
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            return '\n'.join(lines)
        except Exception as e:
            st.error(f"Error scraping URL: {str(e)}")
            return None

class PDFProcessor:
    def process_pdf(self, pdf_file):
        """Extract text from uploaded PDF"""
        text_content = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text_content.append(page.extract_text())
        return '\n'.join(text_content)

class RFPProcessor:
    def __init__(self):
        """Initialize RFP processor with required models"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            st.info("Downloading language model...")
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
            
    def extract_requirements(self, text):
        """Extract requirements from text"""
        doc = self.nlp(text)
        requirements = []
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in 
                  ['required', 'must', 'shall', 'specify', 'requirement', '?']):
                requirements.append({
                    'text': sent.text.strip(),
                    'category': self._categorize_requirement(sent.text),
                    'mandatory': any(word in sent.text.lower() 
                                   for word in ['must', 'shall', 'required'])
                })
        return requirements
    
    def _categorize_requirement(self, text):
        """Categorize requirements into predefined categories"""
        categories = {
            'Technical': ['technical', 'technology', 'system', 'software', 'hardware'],
            'Financial': ['price', 'cost', 'budget', 'financial', 'pricing'],
            'Compliance': ['compliance', 'regulation', 'standard', 'certification'],
            'Experience': ['experience', 'history', 'past performance', 'qualification'],
            'Delivery': ['delivery', 'timeline', 'schedule', 'deadline']
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return 'General'

def main():
    st.set_page_config(page_title="RFP Response Automation", layout="wide")
    
    st.title("RFP Response Automation System")
    
    # Initialize processors
    web_scraper = WebScraper()
    pdf_processor = PDFProcessor()
    rfp_processor = RFPProcessor()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    input_method = st.sidebar.radio(
        "Choose Input Method",
        ["Upload PDF", "Enter URL"]
    )
    
    # Main content area
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload RFP Document", type=['pdf'])
        if uploaded_file:
            with st.spinner("Processing PDF..."):
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    text_content = pdf_processor.process_pdf(tmp_file.name)
                
                # Process requirements
                if text_content:
                    process_content(text_content, rfp_processor)
    
    else:  # URL input
        url = st.text_input("Enter Procurement URL")
        if url and st.button("Process URL"):
            with st.spinner("Scraping URL..."):
                text_content = web_scraper.extract_from_url(url)
                if text_content:
                    process_content(text_content, rfp_processor)

def process_content(text_content, rfp_processor):
    """Process extracted content and display results"""
    # Extract requirements
    requirements = rfp_processor.extract_requirements(text_content)
    
    # Display results in tabs
    tab1, tab2 = st.tabs(["Requirements", "Generated Response"])
    
    with tab1:
        st.subheader("Extracted Requirements")
        for category in set(req['category'] for req in requirements):
            st.write(f"\n### {category}")
            category_reqs = [req for req in requirements if req['category'] == category]
            
            df = pd.DataFrame(category_reqs)
            if not df.empty:
                st.dataframe(
                    df[['text', 'mandatory']].rename(
                        columns={'text': 'Requirement', 'mandatory': 'Mandatory'}
                    )
                )
    
    with tab2:
        st.subheader("Response Generator")
        selected_category = st.selectbox(
            "Select Category to Generate Response",
            options=list(set(req['category'] for req in requirements))
        )
        
        category_reqs = [req for req in requirements if req['category'] == selected_category]
        
        if category_reqs:
            st.write("### Requirements and Responses")
            for req in category_reqs:
                st.text_area(
                    f"Requirement ({'Mandatory' if req['mandatory'] else 'Optional'})",
                    req['text'],
                    key=f"req_{hash(req['text'])}",
                    disabled=True
                )
                response = st.text_area(
                    "Response",
                    "",
                    key=f"resp_{hash(req['text'])}",
                    height=100
                )
        
        if st.button("Save Responses"):
            st.success("Responses saved successfully!")
            # Here you would implement the logic to save responses to your knowledge base

if __name__ == "__main__":
    main()