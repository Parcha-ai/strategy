#!/usr/bin/env python3
"""
Notion Strategy Sync Tool
Bridges Notion strategy workspace with local AI knowledge base
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re
import shutil

class NotionStrategySync:
    """
    Handles synchronization between Notion exports and local knowledge base
    """
    
    def __init__(self, strategy_root: str = "./"):
        self.strategy_root = Path(strategy_root)
        self.kb_root = self.strategy_root / "knowledge-base"
        self.notion_exports = self.kb_root / "sources" / "notion"
        self.notion_exports.mkdir(parents=True, exist_ok=True)
        
    def process_notion_export(self, export_path: str) -> Dict[str, List[str]]:
        """
        Process a Notion export and integrate into knowledge base
        
        Args:
            export_path: Path to unzipped Notion export
            
        Returns:
            Dictionary of processed files by category
        """
        export_path = Path(export_path)
        if not export_path.exists():
            raise FileNotFoundError(f"Export path not found: {export_path}")
            
        processed = {
            "strategies": [],
            "insights": [],
            "decisions": [],
            "research": []
        }
        
        # Process markdown files
        for md_file in export_path.rglob("*.md"):
            category = self._categorize_file(md_file)
            if category:
                processed_path = self._process_markdown_file(md_file, category)
                processed[category].append(str(processed_path))
                
        # Process CSV exports (for databases)
        for csv_file in export_path.rglob("*.csv"):
            self._process_database_export(csv_file)
            
        return processed
    
    def _categorize_file(self, file_path: Path) -> Optional[str]:
        """
        Categorize file based on name and content
        """
        name_lower = file_path.name.lower()
        
        # Check filename patterns
        if any(keyword in name_lower for keyword in ['strategy', 'strategic', 'plan']):
            return "strategies"
        elif any(keyword in name_lower for keyword in ['insight', 'learning', 'discovery']):
            return "insights"
        elif any(keyword in name_lower for keyword in ['decision', 'adr', 'choice']):
            return "decisions"
        elif any(keyword in name_lower for keyword in ['research', 'analysis', 'report']):
            return "research"
            
        # Check content if filename doesn't match
        try:
            content = file_path.read_text()
            if "## Decision" in content or "## Context" in content:
                return "decisions"
            elif "## Insight" in content or "## Finding" in content:
                return "insights"
        except:
            pass
            
        return None
    
    def _process_markdown_file(self, md_file: Path, category: str) -> Path:
        """
        Process and enhance markdown file for knowledge base
        """
        content = md_file.read_text()
        
        # Extract metadata from content
        metadata = self._extract_metadata(content)
        
        # Create knowledge base entry
        kb_entry = self._create_kb_entry(
            title=md_file.stem,
            content=content,
            category=category,
            metadata=metadata
        )
        
        # Determine output path
        if category == "strategies":
            output_dir = self.kb_root / "context" / "current-state"
        elif category == "insights":
            output_dir = self.kb_root / "insights" / "strategic"
        elif category == "decisions":
            output_dir = self.kb_root / "context" / "historical"
        else:  # research
            output_dir = self.kb_root / "sources" / "external"
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write enhanced file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"{md_file.stem}_{timestamp}.yaml"
        
        with open(output_path, 'w') as f:
            yaml.dump(kb_entry, f, default_flow_style=False)
            
        # Also keep original markdown in sources
        notion_archive = self.notion_exports / category
        notion_archive.mkdir(exist_ok=True)
        shutil.copy2(md_file, notion_archive / md_file.name)
        
        return output_path
    
    def _extract_metadata(self, content: str) -> Dict:
        """
        Extract metadata from Notion markdown content
        """
        metadata = {}
        
        # Extract dates
        date_pattern = r'Created:\s*(\d{4}-\d{2}-\d{2})'
        date_match = re.search(date_pattern, content)
        if date_match:
            metadata['created'] = date_match.group(1)
            
        # Extract tags (if present)
        tag_pattern = r'Tags:\s*([^\n]+)'
        tag_match = re.search(tag_pattern, content)
        if tag_match:
            tags = [tag.strip() for tag in tag_match.group(1).split(',')]
            metadata['tags'] = tags
            
        # Extract status
        status_pattern = r'Status:\s*([^\n]+)'
        status_match = re.search(status_pattern, content)
        if status_match:
            metadata['status'] = status_match.group(1).strip()
            
        return metadata
    
    def _create_kb_entry(self, title: str, content: str, category: str, metadata: Dict) -> Dict:
        """
        Create a knowledge base entry in standard format
        """
        # Generate ID
        entry_id = f"{category}-{title.lower().replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}"
        
        # Default tags based on category
        default_tags = {
            "strategies": ["strategic-planning", "business-strategy"],
            "insights": ["insight", "learning"],
            "decisions": ["decision", "architecture"],
            "research": ["research", "analysis"]
        }
        
        tags = metadata.get('tags', []) + default_tags.get(category, [])
        
        entry = {
            'id': entry_id,
            'title': title,
            'type': category.rstrip('s'),  # Remove plural
            'tags': list(set(tags)),  # Unique tags
            'created': metadata.get('created', datetime.now().strftime('%Y-%m-%d')),
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'importance': 'medium',  # Default, should be updated based on content
            'confidence': 'high',  # For Notion exports
            'metadata': {
                'source': 'notion-export',
                'original_file': title,
                **metadata
            },
            'content': content
        }
        
        return entry
    
    def _process_database_export(self, csv_file: Path):
        """
        Process Notion database CSV exports
        """
        # Archive the CSV for reference
        db_archive = self.notion_exports / "databases"
        db_archive.mkdir(exist_ok=True)
        shutil.copy2(csv_file, db_archive / csv_file.name)
        
        print(f"Archived database export: {csv_file.name}")
    
    def create_export_summary(self, processed_files: Dict[str, List[str]]) -> str:
        """
        Create a summary of the export processing
        """
        summary = f"""# Notion Export Processing Summary
        
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Processed Files

### Strategies
{self._format_file_list(processed_files.get('strategies', []))}

### Insights  
{self._format_file_list(processed_files.get('insights', []))}

### Decisions
{self._format_file_list(processed_files.get('decisions', []))}

### Research
{self._format_file_list(processed_files.get('research', []))}

## Next Steps
1. Review categorization accuracy
2. Update importance levels for critical documents
3. Add relationship links between related documents
4. Run knowledge base indexing
"""
        return summary
    
    def _format_file_list(self, files: List[str]) -> str:
        """Format file list for summary"""
        if not files:
            return "- No files processed"
        return "\n".join(f"- {Path(f).name}" for f in files)


def main():
    """
    CLI interface for Notion sync
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Notion exports with knowledge base")
    parser.add_argument("export_path", help="Path to unzipped Notion export")
    parser.add_argument("--summary", action="store_true", help="Print processing summary")
    
    args = parser.parse_args()
    
    sync = NotionStrategySync()
    
    print(f"Processing Notion export from: {args.export_path}")
    processed = sync.process_notion_export(args.export_path)
    
    if args.summary:
        summary = sync.create_export_summary(processed)
        print("\n" + summary)
        
        # Save summary
        summary_path = Path("./knowledge-base/sources/notion/last_import_summary.md")
        summary_path.write_text(summary)
        print(f"\nSummary saved to: {summary_path}")
    
    print(f"\nProcessing complete. Processed {sum(len(v) for v in processed.values())} files.")


if __name__ == "__main__":
    main()