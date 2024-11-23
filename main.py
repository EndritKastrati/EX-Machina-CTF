import os
import autogen
from autogen import ConversableAgent,AssistentAgent,UserProxyAgent
from autogen.coding import DockerCommandLineCodeExecutor,LocalCommandLineCodeExecutor

llm_config_gpt4={
	'cache_seed':None,
	"config_list":[{"model":"gpt-4o","api_key":os.environ["OPENAI_API_KEY"]}]

	'temperature':0.1,
	'timeout'
}

llm_config_gpt35_turbo={
	'cache_seed':None,
	"config_list":[{"model":"gpt-3.5-turbo","api_key":os.environ["OPENAI_API_KEY"]}]
	'temperature':0.1,
	'timeout':6000
}

recon_agent_sysy_msg="""
You are a specialed agent to perform recon against a target
"""


ReconAgent=ConversableAgent(
	"RECONAGENT",
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=False,
	is_termination_msg=lambda x: x.get("content","").rstrip().endswith("TERMINATE"),
	)

 SumAgent=ConversableAgent(
 	"SUMAGENT",
	system_msg=recon_agent_sysy_msg,
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=llm_config_gpt35_turbo,
	is_termination_msg=lambda x: x.get("content","").rstrip().endswith("TERMINATE"),
	default_auto_reply="..."
	)

 exploit_crafter_sys_msg="""
 You are the master command injection exploit crafter. Ensure to adhere to the following principles:
 -Return only the python code in three backticks (```).
 -Ensure to only execute whoami
 -Include 10 different and unique command injecrion payloads
 -Return only the python code in three backticks (```).
 """
 exploit_crafter_Agent= ConversableAgent(
 	"EXPLOITCRAFTAGENT",
 	system_msg=exploit_crafter_sys_msg,
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=llm_config_gpt4,
	is_termination_msg=lambda x: x.get("content","").rstrip().endswith("TERMINATE"),
 	)

executor_Agent= ConversableAgent(
	"EXECAGENT",
	max_consecutive_auto_reply=5,
	human_input_mode ='NEVER',
	llm_config=False,
	is_termination_msg=lambda x: x.get("content","").rstrip().endswith("TERMINATE"),
	code_execution_config={
		"executor":DockerCommandLineCodeExecutor(work_dir="coding",timeout=2048,image="")
		},
	default_auto_reply="..."
 	)

def scrapingtool(url:str):
	response= requests.get(url)
	return(response.text)

register_function(
	scrapingtool,
	caller=ReconAgent,
	executor=SumAgent,
	name='scrpe_page',
	description="Scrape a web page and return the content"
	)

recon_chat=SumAgent.initiate_chat(
	ReconAgent,
	message=f"Can you scrape {target} for me?",
	max_turns=2
	)

result=recon_chat[2]['content']

exploit_chat= executor_Agent.initiate_chat(
	exploit_crafter_Agent,
	meesage=f"Based on this context: {str(result)}, I need you to write a python exploit",
	max_turns=2
	)