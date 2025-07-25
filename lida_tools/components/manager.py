
import os
from typing import List, Union
import logging

import pandas as pd
from llmx import llm, TextGenerator
from lida_tools.datamodel import Goal, Summary, TextGenerationConfig
from lida_tools.utils import read_dataframe
from ..components.summarizer import Summarizer

from ..components.executor import ChartExecutor
from ..components.viz import VizGenerator

import lida_tools.web as lida


logger = logging.getLogger("lida")


class Manager(object):
    def __init__(self, text_gen: TextGenerator = None) -> None:
        """
        Initialize the Manager object.

        Args:
            text_gen (TextGenerator, optional): Text generator object. Defaults to None.
        """

        self.text_gen = text_gen or llm()

        self.summarizer = Summarizer()
        
        self.vizgen = VizGenerator()
        
        self.executor = ChartExecutor()
        
        self.data = None
        self.infographer = None
        

    def check_textgen(self, config: TextGenerationConfig):
        """
        Check if self.text_gen is the same as the config passed in. If not, update self.text_gen.

        Args:
            config (TextGenerationConfig): Text generation configuration.
        """
        if config.provider is None:
            config.provider = self.text_gen.provider or "openai"
            logger.info("Provider is not set, using default provider - %s", config.provider)
            return

        if self.text_gen.provider != config.provider:

            logger.info(
                "Switching Text Generator Provider from %s to %s",
                self.text_gen.provider,
                config.provider)
            self.text_gen = llm(provider=config.provider)

    def summarize(
        self,
        
        data: Union[pd.DataFrame, str],
        file_name="",
        n_samples: int = 1,
        summary_method: str = "columns",
        textgen_config: TextGenerationConfig = TextGenerationConfig(n=1, temperature=0),
    ) -> Summary:
        """
        Summarize data given a DataFrame or file path.

        Args:
            data (Union[pd.DataFrame, str]): Input data, either a DataFrame or file path.
            file_name (str, optional): Name of the file if data is loaded from a file path. Defaults to "".
            n_samples (int, optional): Number of summary samples to generate. Defaults to 3.
            summary_method (str, optional): Summary method to use. Defaults to "default".
            textgen_config (TextGenerationConfig, optional): Text generation configuration. Defaults to TextGenerationConfig(n=1, temperature=0).

        Returns:
            Summary: Summary object containing the generated summary.

        Example of Summary:

            {'name': 'cars.csv',
            'file_name': 'cars.csv',
            'dataset_description': '',
            'fields': [{'column': 'Name',
            'properties': {'dtype': 'string',
                'samples': ['Nissan Altima S 4dr',
                'Mercury Marauder 4dr',
                'Toyota Prius 4dr (gas/electric)'],
                'num_unique_values': 385,
                'semantic_type': '',
                'description': ''}},
            {'column': 'Type',
            'properties': {'dtype': 'category',
                'samples': ['SUV', 'Minivan', 'Sports Car'],
                'num_unique_values': 5,
                'semantic_type': '',
                'description': ''}},
            {'column': 'AWD',
            'properties': {'dtype': 'number',
                'std': 0,
                'min': 0,
                'max': 1,
                'samples': [1, 0],
                'num_unique_values': 2,
                'semantic_type': '',
                'description': ''}},
            }

        """
        self.check_textgen(config=textgen_config)

        #if isinstance(data, str):
            #file_name = data.split("/")[-1]
            #data = read_dataframe(data)

        self.data = data
        return self.summarizer.summarize(
            data=self.data, text_gen=self.text_gen, file_name=file_name,n_samples=n_samples,
            summary_method=summary_method, textgen_config=textgen_config)

    
    def visualize(
        self,
        summary,
        goal,
        textgen_config: TextGenerationConfig = TextGenerationConfig(),
        library="seaborn",
        return_error: bool = False,
    ):
        if isinstance(goal, dict):
            goal = Goal(**goal)
        if isinstance(goal, str):
            goal = Goal(question=goal, visualization=goal, rationale="")

        self.check_textgen(config=textgen_config)
        code_specs = self.vizgen.generate(
            summary=summary, goal=goal, textgen_config=textgen_config, text_gen=self.text_gen,
            library=library)
        charts = self.execute(
            code_specs=code_specs,
            data=self.data,
            summary=summary,
            library=library,
            return_error=return_error,
        )
        return charts

    def execute(
        self,
        code_specs,
        data,
        summary: Summary,
        library: str = "seaborn",
        return_error: bool = False,
    ):

        if data is None:
            root_file_path = os.path.dirname(os.path.abspath(lida.__file__))
            print(root_file_path)
            data = read_dataframe(
                os.path.join(root_file_path, "files/data", summary.file_name)
            )

        # col_properties = summary.properties

        return self.executor.execute(
            code_specs=code_specs,
            data=data,
            summary=summary,
            library=library,
            return_error=return_error,
        )

    