import json
import os
import asyncio
import logging
from pathlib import Path
from scanner.APIClient import APIClient
from scanner.DataExtraction import DataExtract
from scanner.DataSearch import DataSearch


class DLPClient:
    LOGGING_LEVEL = logging.INFO
    ERROR_MISSING_CONFIGURATION_KEY = "Missing configuration key: {}"
    ERROR_PROCESSING_FILE = "Error processing file {}: {}"
    ERROR_DURING_SCAN = "Error during scan: {}"

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.api_client = None
        self.data_search = None
        self.scan_path = Path()
        self.file_types = []
        self.polling_interval = 60
        self.parse_config_file()
        logging.basicConfig(level=self.LOGGING_LEVEL)

    def parse_config_file(self):
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with self.config_path.open('r') as file:
            config = json.load(file)
        try:
            server_url = f"http://{config['Server IP']}:{config['Server Port']}"
            self.api_client = APIClient(server_url)
            self.data_search = DataSearch(config['Custom Searches'])
            self.scan_path = Path(config['Scan Path'])
            self.file_types = config['File Types']
            self.polling_interval = config['Polling Interval']
        except KeyError as e:
            raise ValueError(self.ERROR_MISSING_CONFIGURATION_KEY.format(e))

    async def process_a_file(self, file, root):
        try:
            file_path = Path(root) / file
            data = await DataExtract.from_file(str(file_path))
            results = self.data_search.search(data)
            if results:
                self.api_client.send_data(results)
        except Exception as e:
            logging.error(self.ERROR_PROCESSING_FILE.format(file_path, e))

    async def scan_files_and_process(self):
        for root, dirs, files in os.walk(self.scan_path):
            for file in files:
                if Path(file).suffix[1:] in self.file_types:
                    await self.process_a_file(file, root)

    async def start(self):
        while True:
            try:
                should_run = self.api_client.should_run_scan()
                if should_run:
                    await self.scan_files_and_process()
                    self.api_client.signal_scan_completion()
            except Exception as e:
                logging.error(self.ERROR_DURING_SCAN.format(e))
            await asyncio.sleep(self.polling_interval)


asyncio.run(DLPClient("config.json").start())
