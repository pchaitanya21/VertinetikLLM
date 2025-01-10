import os
import requests
import networkx as nx
import pandas as pd
import geopandas as gpd
import re
from pyvis.network import Network
from IPython.display import display, HTML, Code
from IPython.display import clear_output




from geofunctions import Solution



#this is a global variable that should be used when the call to Solution class is made
isReview = True
'''the output of the LLM is stored in 'response': which has the code for the graph operations for which the next step is
   to generate python code for each node and travaerse the map '''


#Execute the solution graph code generated 

# response_for_graph = Solution.get_LLM_response_for_graph() 

# Solution.graph_response = response
# Solution.save_solution()  #to save the intermediate step of what the graph code is



def generate_function_def(node_name, G):
    '''
    Return a dict, includes two lines: the function definition and return line.
    parameters: operation_node
    '''
    node_dict = G.nodes[node_name]
    node_type = node_dict['node_type']
    
    predecessors = G.predecessors(node_name)
     
    # print("predecessors:", list(predecessors))
    
    # create parameter list with default values
    para_default_str = ''   # for the parameters with the file path
    para_str = ''  # for the parameters without the file path
    for para_name in predecessors:        
        # print("para_name:", para_name)
        para_node = G.nodes[para_name]
        # print(f"para_node: {para_node}")
        # print(para_node)
        data_path = para_node.get('data_path', '')  # if there is a path, the function need to read this file
        
        if data_path != "":            
            para_default_str = para_default_str + f"{para_name}='{data_path}', "
        else:
            para_str = para_str + f"{para_name}={para_name}, "
        
    all_para_str = para_str + para_default_str
    
    function_def = f'{node_name}({all_para_str})'
    function_def = function_def.replace(', )', ')')  # remove the last ","
    
    # generate the return line
    successors = G.successors(node_name) 
    return_str = 'return ' + ', '.join(list(successors))

    
    # print("function_def:", function_def)  # , f"node_type:{node_type}"
    # print("return_str:", return_str)  # , f"node_type:{node_type}"
    # print(function_def, predecessors, successors)
    return_dict = {"function_definition": function_def, 
                   "return_line":return_str, 
                   'description': node_dict['description'], 
                   'node_name': node_name
                  }
    return return_dict

def ask_LLM_to_review_operation_code(self, operation):
        code = operation['operation_code']
        operation_prompt = operation['operation_prompt']
        review_requirement_str = '\n'.join(
            [f"{idx + 1}. {line}" for idx, line in enumerate(constants.operation_review_requirement)])
        review_prompt = f"Your role: {constants.operation_review_role} \n" + \
                          f"Your task: {constants.operation_review_task_prefix} \n\n" + \
                          f"Requirement: \n{review_requirement_str} \n\n" + \
                          f"The code is: \n----------\n{code}\n----------\n\n" + \
                          f"The requirements for the code is: \n----------\n{operation_prompt} \n----------\n"

            # {node_name: "", function_descption: "", function_definition:"", return_line:""
        # operation_prompt:"", operation_code:""}
        print("LLM is reviewing the operation code... \n")
        # print(f"review_prompt:\n{review_prompt}")
        response = helper.get_LLM_reply(prompt=review_prompt,
                                        system_role=constants.operation_review_role,
                                        model=self.model,
                                        verbose=True,
                                        stream=True,
                                        retry_cnt=5,
                                        )
        new_code = helper.extract_code(response)
        reply_content = helper.extract_content_from_LLM_reply(response)
        if (reply_content == "PASS") or (new_code == ""):  # if no modification.
            print("Code review passed, no revision.\n\n")
            new_code = code
        operation['code'] = new_code

        return operation

def initial_operations(self):
        self.operations = []
        operation_names = self.operation_node_names
        for node_name in operation_names:
            function_def_returns = helper.generate_function_def(node_name, self.solution_graph)
            self.operations.append(function_def_returns)


def get_LLM_responses_for_operations(self, review=True):
        # def_list, data_node_list = helper.generate_function_def_list(self.solution_graph)
        self.initial_operations()
        for idx, operation in enumerate(self.operations):
            node_name = operation['node_name']
            print(f"{idx + 1} / {len(self.operations)}, LLM is generating code for operation node: {operation['node_name']}")
            prompt = self.get_prompt_for_an_opearation(operation)

            response = self.get_LLM_reply(
                          prompt=prompt,
                          system_role=constants.operation_role,
                          model=self.model,
                          # model=r"gpt-4",
                         )
            # print(response)
            operation['response'] = response
            try:
                operation_code = helper.extract_code(response=operation['response'], verbose=False)
                # print("operation_code:", operation_code)
            except Exception as e:
                operation_code = ""
            operation['operation_code'] = operation_code

            if review:
                operation = self.ask_LLM_to_review_operation_code(operation)
            
        return self.operations









