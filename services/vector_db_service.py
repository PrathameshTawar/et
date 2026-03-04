"""
Vector Database Service for SatyaSetu
Chroma DB integration with scam detection data
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from config import settings


class VectorDBService:
    """Vector database service for scam detection"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize vector database with sample data"""
        try:
            # Create or load vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
            
            # Check if data already loaded
            collection_count = self.vectorstore._collection.count()
            if collection_count == 0:
                await self.load_scams_data()
            
            self.is_initialized = True
            print(f"✅ Vector DB initialized with {collection_count} documents")
            
        except Exception as e:
            print(f"⚠️ Vector DB initialization error: {e}")
            # Create fresh if error
            self.vectorstore = Chroma.from_texts(
                texts=["init"],
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )
            self.is_initialized = True
    
    async def load_scams_data(self):
        """Load initial scam detection data"""
        
        # Sample scam data - Hindi and English
        scam_data = [
            # Hindi Scams
            {
                "text": "आपके बैंक अकाउंट में समस्या है। तुरंत इस लिंक पर जाकर अपना अपडेट करें: bit.ly/update-bank",
                "language": "hi",
                "type": "phishing",
                "risk_level": "high",
                "source": "RBI_Alert"
            },
            {
                "text": "आप 10 लाख रुपये की सरकारी योजना के लिए योग्य हैं। अभी क्लिक करें और आवेदन करें",
                "language": "hi",
                "type": "government_scheme_scam",
                "risk_level": "high",
                "source": "PIB"
            },
            {
                "text": "आपका आधार कार्ड ब्लॉक हो जाएगा। तुरंत यहाँ क्लिक करके वेरीफाई करें",
                "language": "hi",
                "type": "aadhaar_scam",
                "risk_level": "high",
                "source": "UIDAI_Alert"
            },
            {
                "text": "आपका UPI ID ब्लॉक हो रहा है। अभी KYC अपडेट करें नहीं तो 24 घंटे में ब्लॉक हो जाएगा",
                "language": "hi",
                "type": "upi_scam",
                "risk_level": "high",
                "source": "NPCI_Alert"
            },
            {
                "text": "बधाई हो! आपने 50 लाख रुपये जीते हैं। तुरंत क्लेम करने के लिए 5000 रुपये भेजें",
                "language": "hi",
                "type": "lottery_scam",
                "risk_level": "high",
                "source": "Complaint_Database"
            },
            {
                "text": "आपका मोबाइल नंबर ब्लॉक हो रहा है। तुरंत इस लिंक पर जाकर रिचार्ज करें",
                "language": "hi",
                "type": "mobile_recharge_scam",
                "risk_level": "high",
                "source": "Telecom_Alert"
            },
            {
                "text": "आपका Electricity बिल बकाया है। अभी पेमेंट करें नहीं तो कनेक्शन कट जाएगा",
                "language": "hi",
                "type": "bill_scam",
                "risk_level": "medium",
                "source": "Utility_Scam"
            },
            # English Scams
            {
                "text": "Your bank account has been compromised. Click here to verify your identity: bit.ly/secure-bank",
                "language": "en",
                "type": "phishing",
                "risk_level": "high",
                "source": "RBI_Alert"
            },
            {
                "text": "You've won Rs 50 lakh in a lottery! To claim, send processing fee of Rs 5000",
                "language": "en",
                "type": "lottery_scam",
                "risk_level": "high",
                "source": "Complaint_Database"
            },
            {
                "text": "Your Aadhaar card will be blocked. Verify immediately at this link",
                "language": "en",
                "type": "aadhaar_scam",
                "risk_level": "high",
                "source": "UIDAI_Alert"
            },
            {
                "text": "URGENT: Your UPI account will be suspended. Update KYC now",
                "language": "en",
                "type": "upi_scam",
                "risk_level": "high",
                "source": "NPCI_Alert"
            },
            {
                "text": "Your electricity connection will be disconnected. Pay bill immediately",
                "language": "en",
                "type": "bill_scam",
                "risk_level": "medium",
                "source": "Utility_Scam"
            },
            {
                "text": "Amazon: Your order cannot be delivered. Update payment details",
                "language": "en",
                "type": "phishing",
                "risk_level": "high",
                "source": "Ecommerce_Scam"
            },
            {
                "text": "Netflix: Your account has been suspended. Update payment method",
                "language": "en",
                "type": "phishing",
                "risk_level": "high",
                "source": "Subscription_Scam"
            },
            # Legitimate Messages
            {
                "text": "प्रधानमंत्री किसान सम्मान निधि योजना: सभी पात्र किसानों को प्रति वर्ष 6000 रुपये मिलते हैं। आधिकारिक वेबसाइट पर आवेदन करें",
                "language": "hi",
                "type": "legitimate",
                "risk_level": "low",
                "source": "PIB_Official"
            },
            {
                "text": "RBI has issued new UPI guidelines for payment security. Visit official RBI website for details",
                "language": "en",
                "type": "legitimate",
                "risk_level": "low",
                "source": "RBI_Official"
            },
            {
                "text": "आधार कार्ड के लिए आधिकारिक वेबसाइट uidai.gov.in है। कभी भी अन्य वेबसाइट पर व्यक्तिगत जानकारी न दें",
                "language": "hi",
                "type": "legitimate",
                "risk_level": "low",
                "source": "UIDAI_Official"
            },
            {
                "text": "PM Kisan: Eligible farmers receive Rs 6000 per year. Apply at official pmkisan.gov.in",
                "language": "en",
                "type": "legitimate",
                "risk_level": "low",
                "source": "Government_Official"
            },
            {
                "text": "Cyber Crime Helpline: 1930 for reporting cyber fraud in India",
                "language": "hi",
                "type": "legitimate",
                "risk_level": "low",
                "source": "Govt_Resource"
            },
            {
                "text": "National Cyber Crime Reporting Portal: cybercrime.gov.in for filing complaints",
                "language": "en",
                "type": "legitimate",
                "risk_level": "low",
                "source": "Govt_Resource"
            }
        ]
        
        # Add documents with metadata
        texts = [item["text"] for item in scam_data]
        metadatas = [
            {
                "language": item["language"],
                "type": item["type"],
                "risk_level": item["risk_level"],
                "source": item["source"]
            }
            for item in scam_data
        ]
        
        # Create vector store from documents
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_dir
        )
        
        # Persist to disk
        self.vectorstore.persist()
        
        print(f"✅ Loaded {len(scam_data)} scam samples into vector DB")
    
    async def retrieve_context(
        self,
        query: str,
        k: int = 3,
        language: Optional[str] = None,
        filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve similar scams and guidelines"""
        
        if not self.vectorstore:
            await self.initialize()
        
        # Build filter
        filter_dict = {}
        if language:
            filter_dict["language"] = language
        if filter_type:
            filter_dict["type"] = filter_type
        
        # Search with filters
        if filter_dict:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )
        else:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k
            )
        
        # Format results
        context = []
        for doc, score in results:
            # Convert distance to similarity (lower distance = higher similarity)
            similarity = 1 / (1 + score)
            context.append({
                "text": doc.page_content,
                "similarity": similarity,
                "metadata": doc.metadata
            })
        
        return context
    
    async def get_scam_examples(self, language: str = "hi", limit: int = 10) -> List[Dict[str, Any]]:
        """Get example scams for a language"""
        
        results = await self.retrieve_context(
            query="scam",
            k=limit,
            language=language,
            filter_type="phishing"
        )
        
        return results


# Singleton instance
_vector_db_service: Optional[VectorDBService] = None


def get_vector_db_service() -> VectorDBService:
    """Get or create vector DB service singleton"""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service
