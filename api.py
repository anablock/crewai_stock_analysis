# Standard library imports
from datetime import datetime
import json
from threading import Thread
from uuid import uuid4

# Related third-party imports
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import ValidationError

# Local application/library specific imports
from stock_analysis_agents import StockAnalysisAgents
from stock_analysis_tasks import StockAnalysisTasks
from job_manager import append_event, jobs, jobs_lock, Job, Event
from utils.logging import logger
from crewai import Crew, CrewOutput
from models import StockAnalysisRequest, StockAnalysisResponse, StockAnalysisReport

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow CORS for all origins

def kickoff_crew(job_id: str, company: str):
    logger.info(f"Stock Analysis Crew for job {job_id} is starting")
    try:
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        research_analyst_agent = agents.research_analyst()
        financial_analyst_agent = agents.financial_analyst()
        investment_advisor_agent = agents.investment_advisor()

        research_task = tasks.research(research_analyst_agent, company)
        financial_task = tasks.financial_analysis(financial_analyst_agent)
        filings_task = tasks.filings_analysis(financial_analyst_agent)
        recommend_task = tasks.recommend(investment_advisor_agent)

        crew = Crew(
            agents=[research_analyst_agent, financial_analyst_agent, investment_advisor_agent],
            tasks=[research_task, financial_task, filings_task, recommend_task],
            verbose=True,
        )

        logger.info(f"Crew kickoff for job {job_id} starting")
        result: CrewOutput = crew.kickoff()
        logger.info(f"Crew kickoff for job {job_id} completed")
        logger.debug(f"Raw results for job {job_id}: {result}")

        # Convert results to StockAnalysisReport
        report_dict = {
            "research": result.tasks[0].output,
            "financial_analysis": result.tasks[1].output,
            "filings_analysis": result.tasks[2].output,
            "recommendation": result.tasks[3].output
        }
        report = StockAnalysisReport(**report_dict)
        
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
            jobs[job_id].result = json.dumps(report.dict())
            append_event(job_id, "Stock analysis complete")
        
    except Exception as e:
        logger.error(f"Error in kickoff_crew for job {job_id}: {e}", exc_info=True)
        append_event(job_id, f"An error occurred: {str(e)}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)
    logger.info(f"Stock Analysis Crew for job {job_id} is starting")
    try:
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        research_analyst_agent = agents.research_analyst()
        financial_analyst_agent = agents.financial_analyst()
        investment_advisor_agent = agents.investment_advisor()

        research_task = tasks.research(research_analyst_agent, company)
        financial_task = tasks.financial_analysis(financial_analyst_agent)
        filings_task = tasks.filings_analysis(financial_analyst_agent)
        recommend_task = tasks.recommend(investment_advisor_agent)

        crew = Crew(
            agents=[research_analyst_agent, financial_analyst_agent, investment_advisor_agent],
            tasks=[research_task, financial_task, filings_task, recommend_task],
            verbose=True,
        )

        logger.info(f"Crew kickoff for job {job_id} starting")
        results = crew.kickoff()
        logger.info(f"Crew kickoff for job {job_id} completed")
        logger.debug(f"Raw results for job {job_id}: {results}")

        # Convert results to StockAnalysisReport
        report = StockAnalysisReport(**json.loads(results))
        
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
            jobs[job_id].result = json.dumps(report.dict())
            append_event(job_id, "Stock analysis complete")
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in kickoff_crew for job {job_id}: {e}")
        logger.error(f"Raw results causing error: {results}")
        append_event(job_id, f"An error occurred while parsing results: {str(e)}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)
    except Exception as e:
        logger.error(f"Error in kickoff_crew for job {job_id}: {e}", exc_info=True)
        append_event(job_id, f"An error occurred: {str(e)}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)
    logger.info(f"Stock Analysis Crew for job {job_id} is starting")
    try:
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        research_analyst_agent = agents.research_analyst()
        financial_analyst_agent = agents.financial_analyst()
        investment_advisor_agent = agents.investment_advisor()

        research_task = tasks.research(research_analyst_agent, company)
        financial_task = tasks.financial_analysis(financial_analyst_agent)
        filings_task = tasks.filings_analysis(financial_analyst_agent)
        recommend_task = tasks.recommend(investment_advisor_agent)

        crew = Crew(
            agents=[research_analyst_agent, financial_analyst_agent, investment_advisor_agent],
            tasks=[research_task, financial_task, filings_task, recommend_task],
            verbose=True,
        )

        results = crew.kickoff()
        logger.info(f"Stock Analysis Crew for job {job_id} is complete")
        
        # Convert results to StockAnalysisReport
        report = StockAnalysisReport(**json.loads(results))
        
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
            jobs[job_id].result = json.dumps(report.dict())
            append_event(job_id, "Stock analysis complete")
        
    except Exception as e:
        logger.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {str(e)}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)

@app.route('/api/analyze-stock', methods=['POST'])
def run_crew():
    logger.info("Received request to run stock analysis crew")
    try:
        data = StockAnalysisRequest(**request.json)
    except ValidationError as e:
        logger.error(f"Invalid input data: {e}")
        abort(400, description=f"Invalid input data: {e}")

    job_id = str(uuid4())
    company = data.company
    
    append_event(job_id, "Job created")
    
    thread = Thread(target=kickoff_crew, args=(job_id, company))
    thread.start()
    
    return jsonify({"job_id": job_id}), 202

@app.route('/api/analyze-stock/<job_id>', methods=['GET'])
def get_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if job is None:
        abort(404, description="Job not found")
    
    try:
        result = json.loads(job.result) if job.result else None
        response = StockAnalysisResponse(
            job_id=job_id,
            status=job.status,
            result=StockAnalysisReport(**result) if result and job.status == 'COMPLETE' else None,
            events=[{"timestamp": event.timestamp.isoformat(), "data": event.data} for event in job.events]
        )
        return jsonify(response.dict())
    except ValidationError as e:
        logger.error(f"Error creating response for job {job_id}: {e}")
        abort(500, description="Error processing job result")

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e.description)), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e.description)), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e.description)), 500

if __name__ == '__main__':
    app.run(debug=True, port=3001)