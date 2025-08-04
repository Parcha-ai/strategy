# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the Parcha Strategy repository - a central hub for strategic planning, product roadmaps, market analysis, and business decision-making. Unlike the main Parcha codebase, this repository focuses on documentation, analysis, and strategic artifacts rather than code.

## Repository Structure

- `/docs/strategy/` - Core business and product strategy documents
- `/docs/roadmaps/` - Product roadmaps and feature planning
- `/docs/analysis/` - Market research, competitive analysis, user research
- `/docs/decisions/` - Architecture Decision Records (ADRs) and technical strategy
- `/src/` - Strategy tools, analysis scripts, data processing utilities
- `/templates/` - Standardized templates for strategy documents
- `/notes/` - Working notes, meeting summaries, research snippets
- `/knowledge-base/` - AI-optimized strategic knowledge storage
  - `/entities/` - Core concepts, products, competitors, stakeholders
  - `/insights/` - Technical, strategic, and operational learnings
  - `/context/` - Historical decisions, current state, future plans
  - `/sources/` - Original documents, PDFs, Notion exports

## Key Commands

Since this is primarily a documentation repository, the main commands are:

```bash
# Initialize git repository (if needed)
git init

# View directory structure
tree -L 2

# Search for specific topics
grep -r "keyword" docs/

# Generate document outlines from templates
cp templates/[template-name].md docs/[destination]/
```

## Working with Strategy Documents

When creating or updating strategy documents:

1. **Use Templates**: Start with templates in `/templates/` for consistency
2. **Include Metrics**: Always define success metrics and KPIs
3. **Add Dates**: Include creation and last-modified dates
4. **Link Context**: Reference related documents and decisions
5. **Visual Aids**: Use Mermaid diagrams for flows and architectures

## Document Types and Conventions

### Strategy Documents (`/docs/strategy/`)
- Format: `YYYY-MM-DD-[topic-name].md`
- Include: Executive summary, problem statement, proposed solution, success metrics

### Roadmaps (`/docs/roadmaps/`)
- Format: `[product-area]-roadmap-[quarter].md`
- Include: Timeline, milestones, dependencies, resource requirements

### Analysis (`/docs/analysis/`)
- Format: `[analysis-type]-[subject]-YYYY-MM-DD.md`
- Include: Methodology, findings, recommendations, next steps

### ADRs (`/docs/decisions/`)
- Format: `ADR-[number]-[title].md`
- Follow standard ADR template: Status, Context, Decision, Consequences

## Integration with Main Parcha Codebase

This strategy repository complements the main Parcha development repositories:
- `/Users/aj/dev/parcha/parcha-main/` - Main development
- `/Users/aj/dev/parcha/parcha-backend/` - Backend services
- `/Users/aj/dev/parcha/parcha-fe/` - Frontend application

Reference these repositories when creating technical strategy documents.

## Best Practices

1. **Regular Reviews**: Strategy documents should be reviewed quarterly
2. **Version Control**: Use meaningful commit messages describing strategic changes
3. **Collaboration**: Use pull requests for major strategy updates
4. **Cross-Reference**: Link between related documents
5. **Action Items**: Every strategy document should end with clear next steps

## AI Agent Guidelines

When working on strategic tasks:
- Focus on clarity and actionability over length
- Use data and examples from the main Parcha codebase when relevant
- Create visual diagrams using Mermaid when explaining complex concepts
- Always include success metrics and measurement strategies
- Consider multiple stakeholder perspectives (engineering, product, business)

## Knowledge Base System

### Overview
This repository uses a hybrid Notion + local knowledge base system for strategic intelligence.

### Primary Storage: Notion
The main strategic content lives in Notion at:
- Strategy workspace: https://www.notion.so/Strategy-2450e6162d8080628dd9c32aa14c3e6e

Use Notion for:
- Collaborative strategy development
- Real-time updates and discussions
- Rich media content and embeds
- Database relationships and views

### Local Knowledge Base
The `/knowledge-base/` directory provides AI-optimized storage for:
- Processed strategic insights
- Extracted PDF content
- Cached Notion exports
- Semantic search indices

### Working with Strategic Context

#### 1. Processing PDFs
```bash
python src/pdf_processor.py --input path/to/strategic-doc.pdf
```

#### 2. Syncing Notion Exports
```bash
# Export from Notion: ... → Export → Markdown & CSV
# Then process:
python src/notion_sync.py path/to/notion-export --summary
```

#### 3. Searching Knowledge Base
```bash
python src/kb_retriever.py --query "competitive analysis fintech"
```

### Before Strategic Tasks
1. Check knowledge base for relevant context:
   ```bash
   python src/kb_retriever.py --task "analyze payment provider competition"
   ```

2. If working with new strategic documents:
   - Request Notion export if content is in Notion
   - Process PDFs through pdf_processor
   - Update knowledge base indices

### After Learning Something New
1. Document insights immediately:
   ```bash
   python src/kb_manager.py add --category strategic
   ```

2. Update Notion with significant findings
3. Cross-reference related insights

### Knowledge Base Structure
Each entry follows this format:
```yaml
id: unique-identifier
title: "Clear, descriptive title"
type: concept|insight|decision|analysis
tags: [relevant, semantic, tags]
importance: critical|high|medium|low
confidence: verified|high|medium|low
metadata:
  source: notion|pdf|research|conversation
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
relationships:
  - related-to: other-entry-id
  - implements: concept-id
content: |
  Detailed content in markdown format...
```

### Best Practices
1. Always tag entries with semantic categories
2. Link related insights using relationships
3. Update confidence levels as information is verified
4. Prefer Notion for collaborative content
5. Use local KB for AI processing and analysis
6. Sync important Notion content weekly