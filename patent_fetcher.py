import sqlite3
import requests
import json
import os
import sys
import re
import logging
from datetime import datetime

# Set up logging to a file
logging.basicConfig(filename='patent_fetcher.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

def fetch_patent(api_key, patent_id):
    """Fetch patent data supporting all specified formats"""
    output = {"status": "fetching", "patent_id": patent_id}
    logging.debug(f"Fetching patent data for ID: {patent_id}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Strategy 1: Try lens_id for dashed formats
    if '-' in patent_id and len(patent_id.split('-')) == 5:
        query = {
            "query": {
                "term": {
                    "lens_id": patent_id
                }
            }
        }
        output["search_strategy"] = "lens_id"
        logging.debug("Using lens_id strategy")
    else:
        # Strategy 2: For patent number formats, extract components
        clean_id = re.sub(r'[\s_/]', '', patent_id.upper())
        jurisdiction = None
        doc_number = clean_id
        kind = None

        jurisdiction_match = re.match(r'^([A-Z]{2})(.*)', clean_id)
        if jurisdiction_match:
            jurisdiction = jurisdiction_match.group(1)
            doc_number = jurisdiction_match.group(2)

        kind_match = re.search(r'([A-Z]\d*)$', doc_number)
        if kind_match:
            kind = kind_match.group(1)
            doc_number = doc_number[:-len(kind)]

        numeric_part = re.sub(r'[^0-9]', '', doc_number)
        must_conditions = [{"term": {"doc_number": numeric_part}}]

        if jurisdiction:
            must_conditions.append({"term": {"jurisdiction": jurisdiction}})

        if kind:
            must_conditions.append({"term": {"kind": kind}})

        query = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            }
        }

        output["search_strategy"] = "combined_field"
        output["components"] = {
            "jurisdiction": jurisdiction,
            "doc_number": numeric_part,
            "kind": kind
        }
        logging.debug(f"Using combined_field strategy with components: {output['components']}")

    try:
        response = requests.post(
            "https://api.lens.org/patent/search",
            headers=headers,
            json=query,
            timeout=15
        )

        output["response_status"] = response.status_code
        logging.debug(f"API response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            output["response_body"] = data
            logging.debug(f"API response data: {json.dumps(data, indent=2)}")
            if data.get('total', 0) > 0 and len(data.get('data', [])) > 0:
                patent = data['data'][0]
                output["status"] = "success"
                output["patent_data"] = patent
                output["components"] = {
                    "jurisdiction": patent.get('jurisdiction', 'unknown'),
                    "doc_number": patent.get('doc_number', 'unknown'),
                    "kind": patent.get('kind', 'unknown')
                }
                logging.debug(f"Patent data fetched successfully: {output['components']}")
            else:
                output["status"] = "no_patents_found"
                logging.debug("No patents found")
        else:
            output["status"] = f"error_{response.status_code}"
            output["error_message"] = response.text
            logging.error(f"Error fetching patent data: {response.text}")
    except Exception as e:
        output["status"] = "exception"
        output["error_message"] = str(e)
        logging.error(f"Exception occurred: {str(e)}")

    return output

def save_metadata_to_db(patent):
    """Save patent metadata to the SQLite database"""
    db_path = 'patents.db'  # Reference the database in the same folder
    output = {"status": "saving_metadata"}
    logging.debug(f"Saving metadata to database: {db_path}")

    # Extract required fields from patent data
    lens_id = patent.get('lens_id')

    # Extract title from the nested structure
    title = "Unknown Title"
    if 'biblio' in patent and 'invention_title' in patent['biblio']:
        if patent['biblio']['invention_title'] and len(patent['biblio']['invention_title']) > 0:
            title = patent['biblio']['invention_title'][0].get('text', "Unknown Title")

    # Extract other fields if available
    abstract = patent.get('abstract', '')
    publication_date = patent.get('date_published')

    # These fields might require additional extraction from nested objects
    inventor = None
    filing_date = None
    assignee = None
    pdf_url = None

    # Extract filing date if available in the nested structure
    if 'biblio' in patent and 'application_reference' in patent['biblio']:
        filing_date = patent['biblio']['application_reference'].get('date')

    output["patent_data"] = {
        "lens_id": lens_id,
        "title": title,
        "abstract": abstract,
        "publication_date": publication_date,
        "inventor": inventor,
        "filing_date": filing_date,
        "assignee": assignee,
        "pdf_url": pdf_url
    }

    logging.debug(f"Patent data to be saved: {output['patent_data']}")

    if not lens_id or not title:
        output["status"] = "missing_required_fields"
        logging.error("Missing required fields: lens_id or title")
        return output

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the patent already exists
        cursor.execute('SELECT COUNT(*) FROM patents WHERE id = ?', (lens_id,))
        exists = cursor.fetchone()[0]

        if exists:
            # Update the existing patent record
            cursor.execute('''
                UPDATE patents
                SET title = ?, abstract = ?, publication_date = ?, inventor = ?, filing_date = ?, assignee = ?, pdf_url = ?
                WHERE id = ?
            ''', (
                title,
                abstract,
                publication_date,
                inventor,
                filing_date,
                assignee,
                pdf_url,
                lens_id
            ))
            logging.debug("Patent metadata updated successfully")
        else:
            # Insert a new patent record
            cursor.execute('''
                INSERT INTO patents (id, title, abstract, publication_date, inventor, filing_date, assignee, pdf_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lens_id,
                title,
                abstract,
                publication_date,
                inventor,
                filing_date,
                assignee,
                pdf_url
            ))
            logging.debug("Patent metadata inserted successfully")

        conn.commit()
        conn.close()
        output["status"] = "success"
    except Exception as e:
        output["status"] = "exception"
        output["error_message"] = str(e)
        logging.error(f"Exception occurred while saving metadata: {str(e)}")

    return output

def save_json(output, folder="json_outputs"):
    # Ensure the folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Determine the filename
    filename = "output.json"  # Default filename
    if "fetch_patent" in output and "response_body" in output["fetch_patent"]:
        data = output["fetch_patent"]["response_body"].get("data", [])
        if data:
            patent = data[0]
            jurisdiction = patent.get('jurisdiction', 'unknown')
            doc_number = patent.get('doc_number', 'unknown')
            kind = patent.get('kind', 'unknown')
            filename = f"{jurisdiction}_{doc_number}_{kind}.json"

    filepath = os.path.join(folder, filename)

    with open(filepath, 'w') as outfile:
        json.dump(output, outfile, indent=2)
    logging.debug(f"Output saved to JSON file: {filepath}")

if __name__ == "__main__":
    output = {"runtime_info": {}}
    output["runtime_info"]["current_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output["runtime_info"]["user"] = os.getlogin()
    output["runtime_info"]["script"] = "patent_fetcher.py"
    logging.debug(f"Script started by user: {output['runtime_info']['user']}")

    # Get API key
    api_key = os.environ.get('LENS_API_KEY')
    output["api_key"] = api_key

    if len(sys.argv) > 1 and not sys.argv[1][0].isdigit() and sys.argv[1][0] not in (
    'U', 'E', 'W', 'C', 'J', 'K', 'A', '-'):
        api_key = sys.argv[1]
        patent_idx = 2
    else:
        patent_idx = 1

    if not api_key:
        output["status"] = "error_no_api_key"
        output["usage"] = "python patent_fetcher.py API_KEY PATENT_ID"
        output["supported_formats"] = [
            "EP_0227762_B1_19900411",
            "EP 0227762 B1",
            "EP0227762B1",
            "145-564-229-856-440",
            "US 7,654,321 B2",
            "7,654,321",
            "US8779002B2"
        ]
        save_json(output)
        logging.error("No API key provided")
        sys.exit(1)

    # Get patent ID
    if len(sys.argv) <= patent_idx:
        output["status"] = "error_no_patent_id"
        output["usage"] = "python patent_fetcher.py API_KEY PATENT_ID"
        output["supported_formats"] = [
            "EP_0227762_B1_19900411",
            "EP 0227762 B1",
            "EP0227762B1",
            "145-564-229-856-440",
            "US 7,654,321 B2",
            "7,654,321",
            "US8779002B2"
        ]
        save_json(output)
        logging.error("No patent ID provided")
        sys.exit(1)

    patent_id = sys.argv[patent_idx]

    # Fetch and display patent
    patent_response = fetch_patent(api_key, patent_id)
    output["fetch_patent"] = patent_response

    if patent_response["status"] == "success":
        save_response = save_metadata_to_db(patent_response["patent_data"])
        output["save_metadata"] = save_response

    save_json(output)
    logging.debug("Script completed")
    sys.exit(0)