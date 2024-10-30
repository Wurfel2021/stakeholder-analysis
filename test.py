import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from html import unescape
from urllib.parse import urljoin

class OpenAustraliaAPI:
    def __init__(self, api_key=None, api_url="https://www.openaustralia.org.au/api"):
        """
        Initializes the OpenAustraliaAPI client with the given API key and URL.

        Parameters:
            api_key (str, optional): Your OpenAustralia API key. If not provided,
                                     the class will attempt to load it from the
                                     OPENAUSTRALIA_API_KEY environment variable.
            api_url (str, optional): Base URL for the OpenAustralia API.
                                      Defaults to 'https://www.openaustralia.org.au/api'.
        """
        # Load environment variables from .env file if present
        load_dotenv()

        if not api_key:
            api_key = os.getenv('OPENAUSTRALIA_API_KEY')

        if not api_key:
            raise ValueError("API key not provided. Set it via the api_key parameter or the OPENAUSTRALIA_API_KEY environment variable.")

        self.api_key = api_key
        self.api_url = api_url

    def _make_call(self, function, **kwargs):
        """
        Private method to make API calls using the requests library.

        Parameters:
            function (str): The API function name to call.
            **kwargs: Additional query parameters specific to the API function.

        Returns:
            list/dict: The parsed JSON response from the API if successful.
            None: If an error occurs.
        """
        api_endpoint = f"{self.api_url}/{function}"
        params = {
            'key': self.api_key,
            'output': 'js'  # 'js' stands for JSON
        }

        # Merge additional parameters
        params.update(kwargs)

        try:
            response = requests.get(api_endpoint, params=params)
            
            # Print HTTP status code for debugging
            print(f"HTTP Status Code for '{function}':", response.status_code)
            
            # Print raw response content for debugging
            print(f"Raw response content for '{function}':", response.text)
            
            # Raise an HTTPError if the request was unsuccessful
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Check for API-specific errors
            if isinstance(data, dict) and 'error' in data:
                print(f"API Error in '{function}': {data['error']}")
                return None
            
            return data

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred in '{function}': {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request exception in '{function}': {req_err}")
        except ValueError as json_err:
            print(f"JSON decoding failed in '{function}': {json_err}")
        except Exception as err:
            print(f"An unexpected error occurred in '{function}': {err}")

        return None

    def get_senators(self, date=None, party=None, state=None, search=None, page=None, num=None):
        """
        Fetch a list of Senators.

        Parameters:
            date (str, optional): Fetch the list of Senators as it was on this date (YYYY-MM-DD).
            party (str, optional): Fetch the list of Senators from the given party.
            state (str, optional): Fetch the list of Senators from the given state (NSW, TAS, WA, etc.).
            search (str, optional): Fetch the list of Senators that match this search string in their name.
            page (int, optional): Specify which page of results to return.
            num (int, optional): Specify the number of results per page.

        Returns:
            list: A list of senators if successful, None otherwise.
        """
        data = self._make_call(
            function="getSenators",
            date=date,
            party=party,
            state=state,
            search=search,
            page=page,
            num=num
        )
        
        if isinstance(data, list):
            return data
        else:
            print("No senators found or an error occurred.")
            return None

    def get_senator(self, id=None, person_id=None):
        """
        Fetch details of a specific Senator by id or person_id.

        Parameters:
            id (str, optional): The unique identifier for the Senator.
            person_id (str, optional): Another unique identifier for the Senator.

        Returns:
            dict: Details of the senator if successful, None otherwise.
        """
        # The API expects 'id' as the parameter name
        if person_id:
            print("Warning: The 'getSenator' function expects 'id' as the parameter. 'person_id' will be used as 'id'.")
            id = person_id

        data = self._make_call(
            function="getSenator",
            id=id
        )
        
        if isinstance(data, dict):
            return data
        else:
            print("Senator not found or an error occurred.")
            return None

    def get_representatives(self, postcode=None, date=None, party=None, search=None, page=None, num=None):
        """
        Fetch a list of members of the House of Representatives.

        Parameters:
            postcode (str, optional): Fetch representatives within this postcode.
            date (str, optional): Fetch the list of Representatives as it was on this date (YYYY-MM-DD).
            party (str, optional): Fetch representatives from the given party.
            search (str, optional): Fetch representatives that match this search string in their name.
            page (int, optional): Specify which page of results to return.
            num (int, optional): Specify the number of results per page.

        Returns:
            list: A list of representatives if successful, None otherwise.
        """
        data = self._make_call(
            function="getRepresentatives",
            postcode=postcode,
            date=date,
            party=party,
            search=search,
            page=page,
            num=num
        )
        
        if isinstance(data, list):
            return data
        else:
            print("No representatives found or an error occurred.")
            return None

    def get_representative(self, id=None, division=None, always_return=None):
        """
        Fetch details of a specific Representative by id or division.

        Parameters:
            id (str, optional): The unique identifier for the Representative.
            division (str, optional): The name of the electoral division.
            always_return (bool, optional): If set, always returns a Representative even if the seat is vacant.

        Returns:
            dict: Details of the representative if successful, None otherwise.
        """
        # The API expects 'id' or 'division' as parameters
        if id and division:
            print("Warning: The 'getRepresentative' function should be called with either 'id' or 'division', not both.")
            return None

        data = self._make_call(
            function="getRepresentative",
            id=id,
            division=division,
            always_return=always_return
        )
        
        if isinstance(data, dict):
            return data
        else:
            print("Representative not found or an error occurred.")
            return None

    def get_debates(self, type=None, date=None, search=None, person_id=None, gid=None, year=None, order=None, page=None, num=None):
        """
        Fetch Debates (includes Oral Questions).

        Parameters:
            type (str): One of "representatives" or "senate" (required).
            date (str, optional): Fetch debates from this date (YYYY-MM-DD).
            search (str, optional): Search debates containing this term.
            person_id (str, optional): Fetch debates by this person_id.
            gid (str, optional): Fetch debates by this GID.
            year (int, optional): Fetch debates from this year.
            order (str, optional): Order results by 'd' (date) or 'r' (relevance).
            page (int, optional): Specify which page of results to return.
            num (int, optional): Specify the number of results per page.

        Returns:
            list: A list of debates if successful, None otherwise.
        """
        # The API expects 'type' parameter
        if not type:
            print("Error: The 'type' parameter is required for fetching debates.")
            return None

        if type not in ["representatives", "senate"]:
            print("Invalid type. Must be 'representatives' or 'senate'.")
            return None

        data = self._make_call(
            function="getDebates",
            type=type,
            date=date,
            search=search,
            person_id=person_id,
            gid=gid,
            year=year,
            order=order,
            page=page,
            num=num
        )
        
        if isinstance(data, list):
            return data
        else:
            print("No debates found or an error occurred.")
            return None

    def get_comments(self, date=None, search=None, user_id=None, pid=None, page=None, num=None):
        """
        Fetch comments left on OpenAustralia.

        Parameters:
            date (str, optional): Fetch comments from this date (YYYY-MM-DD).
            search (str, optional): Search comments containing this term.
            user_id (str, optional): Fetch comments by this user ID.
            pid (str, optional): Fetch comments made on this person ID.
            page (int, optional): Specify which page of results to return.
            num (int, optional): Specify the number of results per page.

        Returns:
            list: A list of comments if successful, None otherwise.
        """
        data = self._make_call(
            function="getComments",
            date=date,
            search=search,
            user_id=user_id,
            pid=pid,
            page=page,
            num=num
        )
        
        if isinstance(data, dict) and 'comments' in data:
            return data['comments']
        elif isinstance(data, list):
            return data
        else:
            print("No comments found or an error occurred.")
            return None

    def get_divisions(self, postcode=None, date=None, search=None, page=None, num=None):
        """
        Fetch a list of electoral divisions.

        Parameters:
            postcode (str, optional): Fetch divisions within this postcode.
            date (str, optional): Fetch divisions as they were on this date (YYYY-MM-DD).
            search (str, optional): Search divisions containing this term.
            page (int, optional): Specify which page of results to return.
            num (int, optional): Specify the number of results per page.

        Returns:
            list: A list of divisions if successful, None otherwise.
        """
        data = self._make_call(
            function="getDivisions",
            postcode=postcode,
            date=date,
            search=search,
            page=page,
            num=num
        )
        
        if isinstance(data, list):
            return data
        else:
            print("No divisions found or an error occurred.")
            return None

    def get_hansard(self, search=None, person=None, order=None, page=None, num=None):
        """
        Fetch all Hansard data.

        Parameters:
            search (str, optional): Search Hansard entries containing this term.
            person (str, optional): Fetch Hansard entries by this person ID.
            order (str, optional): Order results by 'd' (date), 'r' (relevance), or 'p' (use by person).
            page (int, optional): Specify which page of results to return.
            num (int, optional): Specify the number of results.

        Returns:
            list: A list of Hansard entries if successful, None otherwise.
        """
        data = self._make_call(
            function="getHansard",
            search=search,
            person=person,  # Changed from 'person_id' to 'person'
            order=order,
            page=page,
            num=num
        )
        
        if isinstance(data, dict) and 'rows' in data:
            return data['rows']
        elif isinstance(data, list):
            return data
        else:
            print("No Hansard entries found or an error occurred.")
            return None
"""
def fetch_full_speech(url):
    try:
        # Unescape the URL
        unescaped_url = unescape(url)
        # Remove fragment identifier
        unescaped_url = unescaped_url.split('#')[0]
        # Ensure the URL uses https
        if not unescaped_url.startswith('http'):
            full_url = f"https://www.openaustralia.org.au{unescaped_url}"
        else:
            full_url = unescaped_url

        print(f"Fetching full speech from {full_url}")
        response = requests.get(full_url)
        response.raise_for_status()

        # Parse the HTML to extract the full speech text
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try different selectors to find the speech content
        # These selectors are based on common patterns; adjust as needed
        speech_div = (
            soup.find('div', {'class': 'speech'}) or
            soup.find('div', {'class': 'speech_text'}) or
            soup.find('div', {'id': 'speech'}) or
            soup.find('div', {'class': 'debate-body'})  # Example alternative
        )
        
        if speech_div:
            full_speech = speech_div.get_text(separator="\n").strip()
            return full_speech
        else:
            # If the expected div is not found, print a snippet of the HTML for debugging
            print(f"Could not find the speech content in the page: {full_url}")
            print("Attempting to extract text from the entire page.")
            full_speech = soup.get_text(separator="\n").strip()
            # Optionally, implement more sophisticated extraction here
            # For now, return the first 1000 characters as a fallback
            snippet = full_speech[:1000]
            print(f"HTML Snippet: {snippet}")
            return full_speech[:1000] + '...'  # Return the first 1000 characters as a fallback
    except Exception as e:
        print(f"Error fetching full speech: {e}")
        return "Unable to retrieve full speech."
"""
def fetch_full_speech(url):
    """
    Fetch the full speech from the provided URL.

    Parameters:
        url (str): The relative or absolute URL to the full speech.

    Returns:
        str: The full speech text if successful, else an error message.
    """
    try:
        # Unescape the URL
        unescaped_url = unescape(url)
        # Remove fragment identifier
        unescaped_url = unescaped_url.split('#')[0]
        # Ensure the URL is absolute
        if not unescaped_url.startswith('http'):
            full_url = urljoin("https://www.openaustralia.org.au", unescaped_url)
        else:
            full_url = unescaped_url

        print(f"Fetching full speech from {full_url}")
        response = requests.get(full_url)
        response.raise_for_status()

        # Parse the HTML to extract the full speech text
        soup = BeautifulSoup(response.content, 'lxml')

        # Inspect the page manually to determine the correct selector
        # Example selectors - these may need to be adjusted based on actual HTML structure
        possible_selectors = [
            {'name': 'div', 'attrs': {'class': 'speech'}},
            {'name': 'div', 'attrs': {'class': 'speech_text'}},
            {'name': 'div', 'attrs': {'id': 'speech'}},
            {'name': 'div', 'attrs': {'class': 'debate-body'}},
            {'name': 'div', 'attrs': {'class': 'speech-content'}},  # Additional example
            {'name': 'div', 'attrs': {'class': 'full-speech'}},      # Additional example
        ]

        speech_div = None
        for selector in possible_selectors:
            speech_div = soup.find(selector['name'], selector['attrs'])
            if speech_div:
                break

        if speech_div:
            full_speech = speech_div.get_text(separator="\n").strip()
            # Clean up the speech text if necessary
            return full_speech
        else:
            # If the expected div is not found, attempt to extract the speech differently
            print(f"Could not find the speech content in the page: {full_url}")
            # As a fallback, extract all text and attempt to isolate the speech
            all_text = soup.get_text(separator="\n").strip()
            # This is a naive approach and may need refinement
            return all_text[:100000] + '...'  # Return the first 1000 characters as a fallback
    except Exception as e:
        print(f"Error fetching full speech from {url}: {e}")
        return "Unable to retrieve full speech."

def export_speeches_to_csv(person_id, filename="hansard_speeches.csv"):
    """
    Fetch Hansard entries for a given person and export them to a CSV file.

    Parameters:
        person_id (str): The ID of the person whose speeches are to be fetched.
        filename (str): The name of the output CSV file. Defaults to "hansard_speeches.csv".
    """
    # Initialize the API client
    try:
        oa_api = OpenAustraliaAPI()
    except ValueError as ve:
        print(ve)
        return

    print(f"\n--- Fetching Hansard Entries for Person ID: {person_id} ---")
    hansard_entries = oa_api.get_hansard(person=person_id)

    if hansard_entries:
        speeches = []
        for entry in hansard_entries:
            hansard_id = entry.get('gid')
            date = entry.get('hdate')
            speaker = entry.get('speaker', {}).get('full_name', 'Unknown')
            body = entry.get('body', 'No content')
            listurl = entry.get('listurl')

            # Construct the full URL
            if listurl:
                # Unescape HTML entities and ensure the URL is absolute
                unescaped_url = unescape(listurl)
                if not unescaped_url.startswith('http'):
                    full_url = urljoin("https://www.openaustralia.org.au", unescaped_url)
                else:
                    full_url = unescaped_url
            else:
                full_url = "No URL available"

            # Initialize full_speech with the body from the API
            full_speech = body

            # Check if the speech is truncated
            # Heuristics:
            # - Speech ends with '...'
            # - Contains HTML entities like '&#'
            # - Speech length is below a threshold (e.g., < 200 characters)
            if body.endswith('...') or '&#' in body or len(body) < 200:
                if listurl:
                    fetched_speech = fetch_full_speech(listurl)
                    full_speech = fetched_speech
                else:
                    full_speech = "Unable to retrieve full speech."

            speeches.append({
                'Hansard ID': hansard_id,
                'Date': date,
                'Speaker': speaker,
                'URL': full_url,
                'Speech': full_speech
            })

        # Convert the list of speeches to a DataFrame
        df = pd.DataFrame(speeches)

        # Export the DataFrame to a CSV file
        df.to_csv(filename, index=False, encoding='utf-8')

        print(f"Speeches have been successfully exported to {filename}.")
    else:
        print("No Hansard entries found or an error occurred.")

# Example usage:
export_speeches_to_csv(person_id="10835", filename="hansard_speeches.csv")


def main():
    # Initialize the API client
    try:
        oa_api = OpenAustraliaAPI()
    except ValueError as ve:
        print(ve)
        return
    # Example 2: Fetch a specific Senator by id
    print("\n--- Example 2: Fetch Senator by id ---")
    senator_id = "10835"  # Replace with a valid id
    senator_details = oa_api.get_senator(id=senator_id)
    if senator_details:
        print(senator_details)
    else:
        print("Senator not found or an error occurred.")
    """
    # Initialize the API client
    try:
        oa_api = OpenAustraliaAPI()
    except ValueError as ve:
        print(ve)
        return
    
    # Example 1: Fetch Senators from NSW belonging to the Australian Labor Party
    print("\n--- Example 1: Fetch Senators from NSW (Australian Labor Party) ---")
    senators = oa_api.get_senators(state="NSW", party="Liberal Party")
    if senators:
        for senator in senators:
            print(f"Name: {senator.get('name')}")
            print(f"Party: {senator.get('party')}")
            print(f"State: {senator.get('constituency')}")
            print(f"Member ID: {senator.get('member_id')}")
            print(f"Person ID: {senator.get('person_id')}")
            print("-" * 40)
    else:
        print("No senators found or an error occurred.")

    # Example 2: Fetch a specific Senator by id
    print("\n--- Example 2: Fetch Senator by id ---")
    senator_id = "10071"  # Replace with a valid id
    senator_details = oa_api.get_senator(id=senator_id)
    if senator_details:
        print(senator_details)
    else:
        print("Senator not found or an error occurred.")

    # Example 3: Fetch Representatives from a specific postcode and party
    print("\n--- Example 3: Fetch Representatives (Postcode: 2000, Party: Australian Labor Party) ---")
    representatives = oa_api.get_representatives(postcode="2000", party="Australian Labor Party")
    if representatives:
        for rep in representatives:
            print(f"Name: {rep.get('name')}")
            print(f"Party: {rep.get('party')}")
            print(f"Division: {rep.get('constituency')}")
            print("-" * 40)
    else:
        print("No representatives found or an error occurred.")

    # Example 4: Fetch a specific Representative by division
    print("\n--- Example 4: Fetch Representative by division ---")
    division = "Sydney"  # Replace with a valid division name
    representative = oa_api.get_representative(division=division)
    if representative:
        print(representative)
    else:
        print("Representative not found or an error occurred.")

    # Example 5: Fetch recent Senate debates containing the term "climate change"
    print("\n--- Example 5: Fetch Senate Debates (Search: 'climate change') ---")
    debates = oa_api.get_debates(type="senate", search="climate change")
    if debates:
        for debate in debates:
            print(f"Debate ID: {debate.get('gid')}")
            print(f"Date: {debate.get('hdate')}")
            print(f"Speaker: {debate.get('speaker', {}).get('full_name')}")
            print(f"Body: {debate.get('body')}")
            print("-" * 40)
    else:
        print("No debates found or an error occurred.")

    # Example 6: Fetch comments about a specific person (person_id)
    print("\n--- Example 6: Fetch Comments (person_id: 10071) ---")
    comments = oa_api.get_comments(pid="10071")
    if comments:
        for comment in comments:
            print(f"Comment ID: {comment.get('comment_id')}")
            print(f"User ID: {comment.get('user_id')}")
            print(f"Body: {comment.get('body')}")
            print(f"Posted: {comment.get('posted')}")
            print("-" * 40)
    else:
        print("No comments found or an error occurred.")

    # Example 7: Fetch electoral divisions by postcode
    print("\n--- Example 7: Fetch Divisions (Postcode: 2000) ---")
    divisions = oa_api.get_divisions(postcode="2000")
    if divisions:
        for division in divisions:
            print(f"Division: {division.get('name')}")
            print("-" * 40)
    else:
        print("No divisions found or an error occurred.")
    
    # Example 8: Fetch Hansard entries related to "education"
    print("\n--- Example 8: Fetch Hansard Entries (Search: 'education') ---")
    hansard_entries = oa_api.get_hansard(person=10044)
    if hansard_entries:
        for entry in hansard_entries:
            print(f"Hansard ID: {entry.get('gid')}")
            print(f"Date: {entry.get('hdate')}")
            speaker = entry.get('speaker', {})
            print(f"Speaker: {speaker.get('full_name')}")
            print(f"Body: {entry.get('body')}")
            print("-" * 40)
    else:
        print("No Hansard entries found or an error occurred.")
    
    # Example usage:
    export_speeches_to_excel(person_id="10835", filename="hansard_speeches.xlsx")
    """

if __name__ == "__main__":
    main()
