#!/usr/bin/env python3
"""
PDF Strategic Document Processor
Extracts and structures content from PDF strategy documents
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import argparse

# Note: In production, you'll need to install these:
# pip install pypdf2 pdfplumber
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("Warning: PDF libraries not installed. Install with:")
    print("pip install pypdf2 pdfplumber")
    sys.exit(1)

class PDFStrategyProcessor:
    """
    Processes PDF documents and extracts strategic intelligence
    """
    
    def __init__(self, kb_root: str = "./knowledge-base"):
        self.kb_root = Path(kb_root)
        self.pdf_archive = self.kb_root / "sources" / "pdfs"
        self.pdf_archive.mkdir(parents=True, exist_ok=True)
        
        # Common strategic keywords for extraction
        self.strategic_keywords = [
            "strategy", "vision", "mission", "objective", "goal", "kpi", "metric",
            "competitive", "market", "analysis", "swot", "risk", "opportunity",
            "roadmap", "milestone", "initiative", "priority", "decision"
        ]
        
    def process_pdf(self, pdf_path: str, title: Optional[str] = None) -> Dict:
        """
        Process a PDF and extract strategic content
        
        Args:
            pdf_path: Path to PDF file
            title: Optional title override
            
        Returns:
            Extracted and structured content
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
        print(f"Processing PDF: {pdf_path.name}")
        
        # Extract content using multiple methods
        text_content = self._extract_text(pdf_path)
        structured_content = self._extract_structured_content(pdf_path)
        
        # Analyze content
        metadata = self._extract_metadata(text_content, pdf_path)
        sections = self._identify_sections(text_content)
        key_points = self._extract_key_points(text_content)
        entities = self._extract_entities(text_content)
        
        # Create knowledge base entry
        kb_entry = self._create_kb_entry(
            title=title or pdf_path.stem,
            content=text_content,
            sections=sections,
            key_points=key_points,
            entities=entities,
            metadata=metadata
        )
        
        # Save processed content
        output_path = self._save_kb_entry(kb_entry, pdf_path)
        
        # Archive original PDF
        archive_path = self.pdf_archive / pdf_path.name
        if not archive_path.exists():
            import shutil
            shutil.copy2(pdf_path, archive_path)
            
        return {
            "kb_entry": kb_entry,
            "output_path": str(output_path),
            "archive_path": str(archive_path)
        }
    
    def _extract_text(self, pdf_path: Path) -> str:
        """
        Extract plain text from PDF
        """
        text_parts = []
        
        try:
            # Try pdfplumber first (better for tables and complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}")
                
        return "\n\n".join(text_parts)
    
    def _extract_structured_content(self, pdf_path: Path) -> Dict:
        """
        Extract tables and structured data from PDF
        """
        structured_data = {
            "tables": [],
            "lists": []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Extract tables
                    tables = page.extract_tables()
                    for j, table in enumerate(tables):
                        if table and len(table) > 1:  # Valid table with data
                            structured_data["tables"].append({
                                "page": i + 1,
                                "table_id": f"page{i+1}_table{j+1}",
                                "headers": table[0] if table else [],
                                "rows": table[1:] if len(table) > 1 else []
                            })
        except Exception as e:
            print(f"Structured extraction error: {e}")
            
        return structured_data
    
    def _extract_metadata(self, content: str, pdf_path: Path) -> Dict:
        """
        Extract metadata from content and file
        """
        metadata = {
            "file_name": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
            "extraction_date": datetime.now().isoformat(),
            "page_count": 0
        }
        
        # Get page count
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata["page_count"] = len(pdf_reader.pages)
        except:
            pass
            
        # Extract dates from content
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content[:1000])  # Check first 1000 chars
            if matches:
                metadata["document_date"] = matches[0]
                break
                
        return metadata
    
    def _identify_sections(self, content: str) -> List[Dict]:
        """
        Identify major sections in the document
        """
        sections = []
        
        # Common section headers
        section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
            r'^(\d+\.?\s+[A-Z].+)$',  # Numbered sections
            r'^([A-Z][a-z\s]+):$'  # Title case with colon
        ]
        
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            is_header = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match and len(line) < 100:  # Reasonable header length
                    is_header = True
                    
                    # Save previous section
                    if current_section:
                        sections.append({
                            "title": current_section,
                            "line_start": section_start,
                            "line_end": i - 1,
                            "preview": ' '.join(section_content[:3])
                        })
                    
                    current_section = match.group(1)
                    section_start = i
                    section_content = []
                    break
            
            if not is_header and current_section:
                section_content.append(line)
        
        # Save last section
        if current_section:
            sections.append({
                "title": current_section,
                "line_start": section_start,
                "line_end": len(lines) - 1,
                "preview": ' '.join(section_content[:3])
            })
            
        return sections
    
    def _extract_key_points(self, content: str) -> List[str]:
        """
        Extract key strategic points from content
        """
        key_points = []
        
        # Look for bullet points, numbered lists, key phrases
        patterns = [
            r'^\s*[-•*]\s+(.+)$',  # Bullet points
            r'^\s*\d+\.\s+(.+)$',   # Numbered lists
            r'(Key\s+(?:finding|point|insight|recommendation)[s]?:\s*.+)',  # Key phrases
            r'(Strategic\s+(?:priority|initiative|goal)[s]?:\s*.+)'
        ]
        
        lines = content.split('\n')
        for line in lines:
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    point = match.group(1).strip()
                    # Filter out very short or very long points
                    if 10 < len(point) < 200:
                        # Check if contains strategic keywords
                        if any(keyword in point.lower() for keyword in self.strategic_keywords):
                            key_points.append(point)
                            
        # Deduplicate while preserving order
        seen = set()
        unique_points = []
        for point in key_points:
            if point.lower() not in seen:
                seen.add(point.lower())
                unique_points.append(point)
                
        return unique_points[:20]  # Top 20 points
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract named entities and concepts
        """
        entities = {
            "companies": [],
            "products": [],
            "technologies": [],
            "metrics": [],
            "dates": [],
            "people": []
        }
        
        # Simple pattern-based extraction
        # In production, consider using NLP libraries like spaCy
        
        # Company patterns (capitalized words, Inc., Ltd., etc.)
        company_pattern = r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*(?:\s+(?:Inc|LLC|Ltd|Corp|Company))?)\b'
        companies = re.findall(company_pattern, content)
        entities["companies"] = list(set(companies))[:10]
        
        # Technology/tool mentions
        tech_keywords = ["API", "AI", "ML", "platform", "system", "tool", "software", "framework"]
        for keyword in tech_keywords:
            pattern = rf'\b(\w+\s+{keyword})\b'
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities["technologies"].extend(matches)
        entities["technologies"] = list(set(entities["technologies"]))[:10]
        
        # Metrics (numbers with units or percentages)
        metric_pattern = r'\b(\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?[MBK]?|\d+(?:\.\d+)?\s*(?:users|customers|revenue|growth))\b'
        metrics = re.findall(metric_pattern, content)
        entities["metrics"] = list(set(metrics))[:10]
        
        return entities
    
    def _create_kb_entry(self, title: str, content: str, sections: List[Dict], 
                        key_points: List[str], entities: Dict, metadata: Dict) -> Dict:
        """
        Create a structured knowledge base entry
        """
        # Determine document type based on content
        doc_type = self._classify_document(content, title)
        
        # Generate tags based on content
        tags = self._generate_tags(content, entities)
        
        entry = {
            "id": f"pdf-{title.lower().replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}",
            "title": title,
            "type": doc_type,
            "tags": tags,
            "created": datetime.now().strftime('%Y-%m-%d'),
            "updated": datetime.now().strftime('%Y-%m-%d'),
            "importance": "medium",  # Default, should be updated based on content
            "confidence": "high",
            "metadata": {
                "source": "pdf",
                "extraction_method": "automated",
                **metadata
            },
            "structure": {
                "sections": sections,
                "key_points": key_points,
                "entities": entities
            },
            "content": content,
            "summary": self._generate_summary(content, key_points)
        }
        
        return entry
    
    def _classify_document(self, content: str, title: str) -> str:
        """
        Classify document type based on content
        """
        content_lower = content.lower()
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["roadmap", "plan", "strategy"]):
            return "strategy"
        elif any(word in content_lower[:1000] for word in ["market analysis", "competitive", "industry"]):
            return "analysis"
        elif any(word in content_lower[:1000] for word in ["decision", "adr", "architecture"]):
            return "decision"
        elif any(word in content_lower[:1000] for word in ["research", "study", "survey"]):
            return "research"
        else:
            return "document"
    
    def _generate_tags(self, content: str, entities: Dict) -> List[str]:
        """
        Generate semantic tags for the document
        """
        tags = []
        content_lower = content.lower()
        
        # Check for strategic concepts
        tag_keywords = {
            "competitive-analysis": ["competitive", "competitor", "market share"],
            "product-strategy": ["product", "feature", "roadmap"],
            "financial-planning": ["revenue", "cost", "budget", "financial"],
            "risk-assessment": ["risk", "threat", "mitigation"],
            "growth-strategy": ["growth", "expansion", "scale"],
            "technical-architecture": ["architecture", "system", "technical"],
            "user-research": ["user", "customer", "research", "feedback"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        # Add entity-based tags
        if entities.get("technologies"):
            tags.append("technical")
        if entities.get("metrics"):
            tags.append("metrics-driven")
            
        return list(set(tags))
    
    def _generate_summary(self, content: str, key_points: List[str]) -> str:
        """
        Generate a brief summary of the document
        """
        # Take first 500 characters
        preview = content[:500].replace('\n', ' ').strip()
        
        # If we have key points, include top 3
        if key_points:
            summary = f"{preview}...\n\nKey Points:\n"
            for point in key_points[:3]:
                summary += f"- {point}\n"
        else:
            summary = f"{preview}..."
            
        return summary
    
    def _save_kb_entry(self, kb_entry: Dict, source_pdf: Path) -> Path:
        """
        Save knowledge base entry to appropriate location
        """
        # Determine output directory based on type
        type_dirs = {
            "strategy": "context/current-state",
            "analysis": "insights/strategic",
            "decision": "context/historical",
            "research": "sources/external",
            "document": "sources/pdfs"
        }
        
        output_dir = self.kb_root / type_dirs.get(kb_entry["type"], "sources/pdfs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as YAML
        output_file = output_dir / f"{kb_entry['id']}.yaml"
        
        # Separate large content into separate file
        if len(kb_entry.get("content", "")) > 5000:
            content_file = output_dir / f"{kb_entry['id']}_content.md"
            content_file.write_text(kb_entry["content"])
            kb_entry["content_file"] = str(content_file.relative_to(self.kb_root))
            kb_entry["content"] = kb_entry["summary"]  # Keep summary in YAML
        
        with open(output_file, 'w') as f:
            yaml.dump(kb_entry, f, default_flow_style=False, sort_keys=False)
            
        return output_file


def main():
    """
    CLI interface for PDF processing
    """
    parser = argparse.ArgumentParser(description="Process strategic PDF documents")
    parser.add_argument("--input", "-i", required=True, help="Path to PDF file")
    parser.add_argument("--title", "-t", help="Override document title")
    parser.add_argument("--kb-root", default="./knowledge-base", help="Knowledge base root directory")
    
    args = parser.parse_args()
    
    processor = PDFStrategyProcessor(kb_root=args.kb_root)
    
    try:
        result = processor.process_pdf(args.input, title=args.title)
        
        print(f"\nProcessing complete!")
        print(f"Knowledge base entry: {result['output_path']}")
        print(f"PDF archived at: {result['archive_path']}")
        
        # Print summary
        kb_entry = result["kb_entry"]
        print(f"\nDocument Summary:")
        print(f"- Title: {kb_entry['title']}")
        print(f"- Type: {kb_entry['type']}")
        print(f"- Tags: {', '.join(kb_entry['tags'])}")
        print(f"- Sections found: {len(kb_entry['structure']['sections'])}")
        print(f"- Key points extracted: {len(kb_entry['structure']['key_points'])}")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())