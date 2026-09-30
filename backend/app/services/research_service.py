from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models import models
from .search_service import SearchService
from .extraction_service import ExtractionService
from .ai_service import AIService
from .credit_service import CreditService


class ResearchService:
    @staticmethod
    def process_research_job(job_id: int):
        db: Session = SessionLocal()
        try:
            job = db.query(models.ResearchJob).filter(
                models.ResearchJob.id == job_id
            ).first()
            if not job:
                return

            # ── Step 1: Search Wikipedia ────────────
            job.status = "searching"
            db.commit()

            search_results = SearchService.search_news(
                topic=job.topic, 
                content_type=job.content_type, 
                time_range=job.time_range
            )
            
            if not search_results:
                raise Exception("Search returned no results.")
                
            # Create source records
            for res in search_results:
                src = models.Source(
                    research_job_id=job.id,
                    url=res["link"],
                    title=res["title"]
                )
                db.add(src)
            db.commit()

            # ── Step 2: Extract & Clean ────────────
            job.status = "extracting"
            db.commit()
            
            extracted_articles = []
            sources = db.query(models.Source).filter(models.Source.research_job_id == job.id).all()
            
            for source in sources:
                extraction = ExtractionService.extract_article(source.url)
                source.extraction_status = extraction["status"]
                source.content = extraction["content"]
                if extraction["status"] == "success":
                    extracted_articles.append({
                        "url": source.url,
                        "title": source.title,
                        "content": source.content
                    })
            db.commit()
            
            if not extracted_articles:
                raise Exception("Failed to extract content from any sources.")
            
            unique_articles = ExtractionService.deduplicate_articles(extracted_articles)

            # ── Step 3: AI Fact Extraction & Report Synthesis ────────────
            job.status = "analyzing"
            db.commit()

            research_text = AIService.research_topic(
                topic=job.topic,
                content_type=job.content_type,
                articles=unique_articles
            )

            job.final_report = research_text
            db.commit()

            # ── Step 4: Generate script ─────────────────────────────────
            script = AIService.generate_script(
                topic=job.topic,
                research_text=research_text,
                content_type=job.content_type,
            )

            job.final_script = script
            
            # ── Step 5: Generate PDF ────────────────────────────────────
            from ..utils.pdf_generator import generate_pdf_script
            import os
            
            pdf_filename = f"script_{job.id}.pdf"
            generate_pdf_script(
                topic=job.topic,
                content_type=job.content_type,
                script_text=script,
                filename=pdf_filename
            )
            job.pdf_path = f"/exports/{pdf_filename}"
            
            job.status = "completed"
            db.commit()
            print(f"Job {job_id} completed successfully.")

        except Exception as e:
            print(f"Job {job_id} failed: {e}")
            db.rollback()
            job = db.query(models.ResearchJob).filter(
                models.ResearchJob.id == job_id
            ).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                db.commit()
                CreditService.refund_credits(db, job_id, str(e))
        finally:
            db.close()
