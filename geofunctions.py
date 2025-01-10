import LLM_Geo_Constants as constants
import helper
import os
import requests
import networkx as nx
import pandas as pd
import geopandas as gpd
# from pyvis.network import Network
from openai import OpenAI
import configparser
import pickle
import time
import sys
import traceback
import vertexai


config = configparser.ConfigParser()
config.read('config.ini')

# use your KEY.
PROJECT_ID = config.get('API_Key', 'PROJECT_ID')
LOCATION = config.get('Location', 'LOCATION_ID')
vertexai.init(project=PROJECT_ID, location=LOCATION)

class Solution():
  
    def __init__(self, 
                 task, 
                 task_name,
                 save_dir,                
                 role=constants.graph_role,
                 model=r"gpt-4o",
                 data_locations=[],
                 stream=True,
                 verbose=True,
                ):        
        self.task = task        
        self.solution_graph = None
        self.graph_response = None
        self.role = role
        self.data_locations=data_locations
        self.task_name = task_name   
        self.save_dir = save_dir
        self.code_for_graph = ""
        self.graph_file = os.path.join(self.save_dir, f"{self.task_name}.graphml")
        self.source_nodes = None
        self.sink_nodes = None
        self.operations = []  # each operation is an element:
        # {node_name: "", function_descption: "", function_definition:"", return_line:""
        # operation_prompt:"", operation_code:""}
        self.assembly_prompt = ""
        
        self.parent_solution = None
        self.model = model
        self.stream = stream
        self.verbose = verbose

        self.assembly_LLM_response = ""
        self.code_for_assembly = ""
        self.graph_prompt = ""
         
        self.data_locations_str = '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(self.data_locations)])     
        
        graph_requirement = constants.graph_requirement.copy()
        graph_requirement.append(f"Save the network into GraphML format, save it at: {self.graph_file}")
        graph_requirement_str =  '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(graph_requirement)])
        
        graph_prompt = f'Your role: {self.role} \n\n' + \
               f'Your task: {constants.graph_task_prefix} \n {self.task} \n\n' + \
               f'Your reply needs to meet these requirements: \n {graph_requirement_str} \n\n' + \
               f'Your reply example: {constants.graph_reply_exmaple} \n\n' + \
               f'Data locations (each data is a node): {self.data_locations_str} \n'
        self.graph_prompt = graph_prompt

        # self.direct_request_prompt = ''
        self.direct_request_LLM_response = ''
        self.direct_request_code = ''

        self.chat_history = [{'role': 'system', 'content': role}]

    def get_LLM_reply(self,
            prompt,
            verbose=True,
            temperature=1,
            stream=True,
            retry_cnt=3,
            sleep_sec=10,
            system_role=None,
            model=None,
            ):


        if system_role is None:
            system_role = self.role

        if model is None:
            model = self.model

        # Query ChatGPT with the prompt
        # if verbose:
        #     print("Geting LLM reply... \n")
        count = 0
        isSucceed = False
        self.chat_history.append({'role': 'user', 'content': prompt})
        while (not isSucceed) and (count < retry_cnt):
            try:
                count += 1
                response = client.chat.completions.create(model=model,
                # messages=self.chat_history,  # Too many tokens to run.
                messages=[
                            {"role": "system", "content": system_role},
                            {"role": "user", "content": prompt},
                          ],
                temperature=temperature,
                stream=stream)
            except Exception as e:
                # logging.error(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
                print(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n",
                      e)
                time.sleep(sleep_sec)

        response_chucks = []
        if stream:
            for chunk in response:
                response_chucks.append(chunk)
                content = chunk.choices[0].delta.content
                if content is not None:
                    if verbose:
                        print(content, end='')
        else:
            content = response.choices[0].message.content
            # print(content)
        print('\n\n')
        # print("Got LLM reply.")

        response = response_chucks  # good for saving

        content = helper.extract_content_from_LLM_reply(response)

        self.chat_history.append({'role': 'assistant', 'content': content})

        return response
    
    def get_LLM_reply(self,
            prompt,
            verbose=True,
            temperature=1,
            stream=True,
            retry_cnt=3,
            sleep_sec=10,
            system_role=None,
            model=None,
            ):


        if system_role is None:
            system_role = self.role

        if model is None:
            model = self.model

        # Query ChatGPT with the prompt
        # if verbose:
        #     print("Geting LLM reply... \n")
        count = 0
        isSucceed = False
        self.chat_history.append({'role': 'user', 'content': prompt})
        while (not isSucceed) and (count < retry_cnt):
            try:
                count += 1
                response = client.chat.completions.create(model=model,
                # messages=self.chat_history,  # Too many tokens to run.
                messages=[
                            {"role": "system", "content": system_role},
                            {"role": "user", "content": prompt},
                          ],
                temperature=temperature,
                stream=stream)
            except Exception as e:
                # logging.error(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
                print(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n",
                      e)
                time.sleep(sleep_sec)

        response_chucks = []
        if stream:
            for chunk in response:
                response_chucks.append(chunk)
                content = chunk.choices[0].delta.content
                if content is not None:
                    if verbose:
                        print(content, end='')
        else:
            content = response.choices[0].message.content
            # print(content)
        print('\n\n')
        # print("Got LLM reply.")

        response = response_chucks  # good for saving

        content = helper.extract_content_from_LLM_reply(response)

        self.chat_history.append({'role': 'assistant', 'content': content})

        return response


    def get_LLM_response_for_graph(self, execuate=True):
        # self.chat_history.append()
        response = self.get_LLM_reply(
                                        prompt=self.graph_prompt,
                                        system_role=self.role,
                                        model=self.model,
                                         )
        self.graph_response = response
        try:
            self.code_for_graph = helper.extract_code(response=self.graph_response, verbose=False)
        except Exception as e:
            self.code_for_graph = ""
            print("Extract graph Python code rom LLM failed.")
        if execuate:
            exec(self.code_for_graph)
            self.load_graph_file()
        return self.graph_response
        
    def load_graph_file(self, file=""):
        G = None
        if os.path.exists(file):
            self.graph_file = file
            G = nx.read_graphml(self.graph_file)
        else:
            
            if file == "" and os.path.exists(self.graph_file):
                G = nx.read_graphml(self.graph_file)
            else:
                print("Do not find the given graph file:", file)
                return None
        
        self.solution_graph = G
        
        self.source_nodes = helper.find_source_node(self.solution_graph)
        self.sink_nodes = helper.find_sink_node(self.solution_graph)
         
        return self.solution_graph 

    @property
    def operation_node_names(self):
        opera_node_names = []
        assert self.solution_graph, "The Soluction class instance has no solution graph. Please generate the graph"
        for node_name in self.solution_graph.nodes():
            node = self.solution_graph.nodes[node_name]
            if node['node_type'] == 'operation':
                opera_node_names.append(node_name)
        return opera_node_names

    def get_ancestor_operations(self, node_name):
        ancestor_operation_names = []
        ancestor_node_names = nx.ancestors(self.solution_graph, node_name)
        # for ancestor_node_name in ancestor_node_names:
        ancestor_operation_names = [node_name for node_name in ancestor_node_names if node_name in self.operation_node_names]

        ancestor_operation_nodes = []
        for oper in self.operations:
            oper_name = oper['node_name']
            if oper_name in ancestor_operation_names:
                ancestor_operation_nodes.append(oper)

        return ancestor_operation_nodes

    def get_descendant_operations(self, node_name):
        descendant__operation_names = []
        descendant_node_names = nx.descendants(self.solution_graph, node_name)
        # for descendant_node_name in descendant_node_names:
        descendant__operation_names = [node_name for node_name in descendant_node_names if node_name in self.operation_node_names]
        # descendant_codes = '\n'.join([oper['operation_code'] for oper in descendant_node_names])
        descendant_operation_nodes = []
        for oper in self.operations:
            oper_name = oper['node_name']
            if oper_name in descendant__operation_names:
                descendant_operation_nodes.append(oper)

        return descendant_operation_nodes

    def get_descendant_operations_definition(self, descendant_operations):

        keys = ['node_name', 'description', 'function_definition', 'return_line']
        operation_def_list = []
        for node in descendant_operations:
            operation_def = {key: node[key] for key in keys}
            operation_def_list.append(str(operation_def))
        defs = '\n'.join(operation_def_list)
        return defs

    def get_prompt_for_an_opearation(self, operation):
        assert self.solution_graph, "Do not find solution graph!"
        # operation_dict = function_def.copy()

        node_name = operation['node_name']

        # get ancestors code
        ancestor_operations = self.get_ancestor_operations(node_name)
        ancestor_operation_codes = '\n'.join([oper['operation_code'] for oper in ancestor_operations])
        descendant_operations = self.get_descendant_operations(node_name)
        descendant_defs = self.get_descendant_operations_definition(descendant_operations)
        descendant_defs_str = str(descendant_defs)

        pre_requirements = [
            f'The function description is: {operation["description"]}',
            f'The function definition is: {operation["function_definition"]}',
            f'The function return line is: {operation["return_line"]}'
        ]

        operation_requirement_str = '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(
            pre_requirements + constants.operation_requirement)])

        operation_prompt = f'Your role: {constants.operation_role} \n\n' + \
                           f'operation_task: {constants.operation_task_prefix} {operation["description"]} \n\n' + \
                           f'This function is one step to solve the question/task: {self.task} \n\n' + \
                           f"This function is a operation node in a solution graph for the question/task, the Python code to build the graph is: \n{self.code_for_graph} \n\n" + \
                           f'Data locations: {self.data_locations_str} \n\n' + \
                           f'Your reply example: {constants.operation_reply_exmaple} \n\n' + \
                           f'Your reply needs to meet these requirements: \n {operation_requirement_str} \n\n' + \
                           f"The ancestor function code is (need to follow the generated file names and attribute names): \n {ancestor_operation_codes} \n\n" + \
                           f"The descendant function (if any) definitions for the question are (node_name is function name): \n {descendant_defs_str}"

        operation['operation_prompt'] = operation_prompt
        return operation_prompt